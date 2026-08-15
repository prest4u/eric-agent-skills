#!/usr/bin/env python3
import importlib.util
import os
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_pptx.py"
SPEC = importlib.util.spec_from_file_location("export_pptx", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ExportPptxTests(unittest.TestCase):
    def test_output_target_defaults_to_project_boundary(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            project = root / "project"
            project.mkdir()
            manifest = project / "deck.pptd"
            manifest.touch()

            target = MODULE.resolve_output_target(
                manifest, project / "out" / "deck.pptx", kind="pptx"
            )
            self.assertEqual(target, (project / "out" / "deck.pptx").resolve())
            with self.assertRaisesRegex(MODULE.OutputSafetyError, "outside the PPTD project"):
                MODULE.resolve_output_target(
                    manifest, root / "external.pptx", kind="pptx"
                )
            with self.assertRaisesRegex(MODULE.OutputSafetyError, "project directory"):
                MODULE.resolve_output_target(manifest, project, kind="directory")

    def test_external_opt_in_allows_only_new_target(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            project = root / "project"
            project.mkdir()
            manifest = project / "deck.pptd"
            manifest.touch()
            external = root / "external.pptx"

            target = MODULE.resolve_output_target(
                manifest,
                external,
                kind="pptx",
                allow_outside_project=True,
            )
            self.assertEqual(target, external.resolve())
            external.touch()
            with self.assertRaisesRegex(MODULE.OutputSafetyError, "existing output outside"):
                MODULE.resolve_output_target(
                    manifest,
                    external,
                    kind="pptx",
                    allow_outside_project=True,
                )

    def test_output_target_rejects_symlink_components(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            project = root / "project"
            external = root / "external"
            project.mkdir()
            external.mkdir()
            manifest = project / "deck.pptd"
            manifest.touch()
            link = project / "linked-output"
            link.symlink_to(external, target_is_directory=True)

            with self.assertRaises(MODULE.OutputSafetyError):
                MODULE.resolve_output_target(
                    manifest, link / "deck.pptx", kind="pptx"
                )

    def test_pptx_target_rejects_manifest_and_non_pptx_extensions(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            with self.assertRaisesRegex(MODULE.OutputSafetyError, r"\.pptx extension"):
                MODULE.resolve_output_target(manifest, manifest, kind="pptx")
            with self.assertRaisesRegex(MODULE.OutputSafetyError, r"\.pptx extension"):
                MODULE.resolve_output_target(
                    manifest, project / "pages" / "slide.page", kind="pptx"
                )

    def test_pptx_target_rejects_page_even_when_page_uses_pptx_suffix(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            page = project / "slide.pptx"
            page.write_text("elements: []\n", encoding="utf-8")
            manifest = project / "deck.pptd"
            manifest.write_text(
                "version: v2\npages:\n  - slide.pptx\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(MODULE.OutputSafetyError, "input file"):
                MODULE.resolve_output_target(manifest, page, kind="pptx")

    def test_no_clobber_commit_preserves_target_that_appeared(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            staged = root / ".staged.pptx"
            output = root / "deck.pptx"
            staged.write_bytes(b"new")
            output.write_bytes(b"competitor")
            with self.assertRaisesRegex(MODULE.OutputSafetyError, "appeared during export"):
                MODULE.commit_staged_file(staged, output, replace_existing=False)
            self.assertEqual(output.read_bytes(), b"competitor")
            self.assertEqual(staged.read_bytes(), b"new")

    def test_local_export_does_not_fall_back_after_output_safety_error(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            project = root / "project"
            project.mkdir()
            manifest = project / "deck.pptd"
            manifest.touch()
            with patch.object(MODULE, "build_payload") as build_payload:
                with self.assertRaises(MODULE.OutputSafetyError):
                    MODULE.export_pptx(
                        manifest,
                        root / "external.pptx",
                        "fade",
                        True,
                    )
            build_payload.assert_not_called()

    def test_local_export_stages_before_replacing_existing_output(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            manifest = root / "deck.pptd"
            manifest.touch()
            exporter = root / "portable_ooxml.py"
            exporter.touch()
            output = root / "deck.pptx"
            output.write_bytes(b"old")

            def write_staged(command, **_kwargs):
                staged = Path(command[command.index("-o") + 1])
                self.assertNotEqual(staged, output)
                staged.write_bytes(b"new")
                return MODULE.subprocess.CompletedProcess(command, 0, "ok")

            with patch.object(MODULE, "PORTABLE_EXPORTER", exporter), \
                    patch.object(MODULE.subprocess, "run", side_effect=write_staged), \
                    patch.object(MODULE, "patch_transitions", return_value=1), \
                    patch.object(MODULE, "verify_output", return_value={"ok": True}):
                summary = MODULE.export_pptx_local(
                    manifest, output, "fade", force=True
                )

            self.assertEqual(output.read_bytes(), b"new")
            self.assertEqual(summary["output"], str(output.resolve()))
            self.assertFalse(any(root.glob(".*.tmp.pptx")))

    def test_failed_local_export_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            manifest = root / "deck.pptd"
            manifest.touch()
            exporter = root / "portable_ooxml.py"
            exporter.touch()
            output = root / "deck.pptx"
            output.write_bytes(b"old")

            def fail_after_partial_write(command, **_kwargs):
                Path(command[command.index("-o") + 1]).write_bytes(b"partial")
                return MODULE.subprocess.CompletedProcess(command, 1, "failed")

            with patch.object(MODULE, "PORTABLE_EXPORTER", exporter), \
                    patch.object(MODULE.subprocess, "run", side_effect=fail_after_partial_write):
                with self.assertRaisesRegex(MODULE.ExportError, "portable OOXML export failed"):
                    MODULE.export_pptx_local(manifest, output, "fade", force=True)

            self.assertEqual(output.read_bytes(), b"old")
            self.assertFalse(any(root.glob(".*.tmp.pptx")))

    def test_parse_agent_browser_version(self):
        self.assertEqual(MODULE.parse_version("agent-browser 0.33.2"), (0, 33, 2))
        self.assertEqual(MODULE.parse_version("v1.4.0-beta.1"), (1, 4, 0))

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_old_agent_browser_exits_without_installing(self, which, run_command):
        which.side_effect = [
            "/bin/node",
            "/bin/npm",
            "/bin/agent-browser",
        ]
        run_command.side_effect = [
            MODULE.subprocess.CompletedProcess([], 0, "v22.11.0\n"),
            MODULE.subprocess.CompletedProcess([], 0, "agent-browser 0.17.1\n"),
        ]
        with self.assertRaisesRegex(MODULE.ExportError, "does not install global packages"):
            MODULE.ensure_agent_browser()
        self.assertEqual(len(run_command.call_args_list), 2)

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_missing_nodejs_raises_clear_error(self, which, run_command):
        which.return_value = None
        with self.assertRaisesRegex(MODULE.ExportError, "Node.js is not installed"):
            MODULE.ensure_nodejs()
        run_command.assert_not_called()

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_old_nodejs_raises_clear_error(self, which, run_command):
        which.return_value = "/bin/node"
        run_command.return_value = MODULE.subprocess.CompletedProcess([], 0, "v16.20.2\n")
        with self.assertRaisesRegex(MODULE.ExportError, "Node.js 18\\+ is required"):
            MODULE.ensure_nodejs()

    @patch.object(MODULE, "run_command")
    @patch.object(MODULE.shutil, "which")
    def test_missing_npm_raises_clear_error(self, which, run_command):
        which.side_effect = ["/bin/node", None]
        run_command.return_value = MODULE.subprocess.CompletedProcess([], 0, "v22.11.0\n")
        with self.assertRaisesRegex(MODULE.ExportError, "npm is not installed"):
            MODULE.ensure_nodejs()

    def test_parse_node_version(self):
        self.assertEqual(MODULE.parse_node_version("v22.11.0"), (22, 11, 0))
        self.assertEqual(MODULE.parse_node_version("18.20.4"), (18, 20, 4))

    def test_fade_is_inserted_before_timing(self):
        source = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<p:sld xmlns:p="urn:test"><p:cSld><p:spTree><p:extLst/>'
            b'</p:spTree></p:cSld><p:clrMapOvr/><p:timing/><p:extLst/></p:sld>'
        )
        result_bytes = MODULE.replace_transition(source, "fade")
        result = result_bytes.decode("utf-8")
        self.assertIn("<p:transition", result)
        self.assertIn("<p:fade/>", result)
        self.assertGreater(result.index("<p:transition"), result.index("<p:clrMapOvr"))
        self.assertLess(result.index("<p:transition"), result.index("<p:timing"))
        MODULE.validate_transition_order(result_bytes, "fade")

    def test_existing_transition_is_replaced_or_removed(self):
        source = (
            b'<p:sld xmlns:p="urn:test"><p:cSld/>'
            b'<p:transition><p:wipe/></p:transition><p:extLst/></p:sld>'
        )
        faded = MODULE.replace_transition(source, "fade").decode("utf-8")
        self.assertNotIn("p:wipe", faded)
        self.assertEqual(faded.count("<p:transition"), 1)
        MODULE.validate_transition_order(faded.encode("utf-8"), "fade")
        cleared = MODULE.replace_transition(source, "none").decode("utf-8")
        self.assertNotIn("p:transition", cleared)
        MODULE.validate_transition_order(cleared.encode("utf-8"), "none")

    def test_nested_transition_is_relocated_to_slide_root(self):
        source = (
            b'<p:sld xmlns:p="urn:test"><p:cSld><p:spTree>'
            b'<p:transition><p:fade/></p:transition><p:extLst/>'
            b'</p:spTree></p:cSld><p:clrMapOvr/><p:extLst/></p:sld>'
        )
        result = MODULE.replace_transition(source, "fade")
        MODULE.validate_transition_order(result, "fade")
        self.assertEqual(MODULE.root_child_names(result), [
            "cSld", "clrMapOvr", "transition", "extLst"
        ])

    def test_patch_transitions_preserves_a_valid_zip(self):
        with tempfile.TemporaryDirectory() as name:
            deck = Path(name) / "test.pptx"
            with zipfile.ZipFile(deck, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "[Content_Types].xml",
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Override PartName="/ppt/presentation.xml" '
                    f'ContentType="{MODULE.PPTX_CONTENT_TYPE}"/></Types>',
                )
                archive.writestr("ppt/presentation.xml", "<p:presentation xmlns:p=\"urn:test\"/>")
                archive.writestr(
                    "ppt/slides/slide1.xml",
                    '<p:sld xmlns:p="urn:test"><p:cSld/></p:sld>',
                )
                archive.writestr(
                    "customXml/provenance.xml",
                    '<provenance xmlns="urn:legacy:pptd:provenance">'
                    '<producer>Legacy Producer</producer>'
                    '<statement>Built by a legacy producer</statement>'
                    '</provenance>',
                )
            self.assertEqual(MODULE.patch_transitions(deck, "fade"), 1)
            with zipfile.ZipFile(deck) as archive:
                self.assertIsNone(archive.testzip())
                slide = archive.read("ppt/slides/slide1.xml")
                self.assertIn(b"<p:fade/>", slide)
                provenance = archive.read("customXml/provenance.xml")
                self.assertIn(b"urn:eric:pptd:provenance", provenance)
                self.assertIn(b"<producer>Eric PPT Skill</producer>", provenance)
                self.assertIn(b"Built by Eric PPT Skill with PPTD", provenance)

    @patch.object(MODULE.subprocess, "call", return_value=0)
    def test_run_command_captures_utf8_via_temp_file(self, call):
        def write_sink(*_args, **kwargs):
            kwargs["stdout"].write("agent-browser 0.33.2\n")
            return 0

        call.side_effect = write_sink
        process = MODULE.run_command(["agent-browser", "--version"], timeout=5)
        self.assertEqual(process.returncode, 0)
        self.assertIn("0.33.2", process.stdout)
        self.assertEqual(call.call_args.kwargs["stderr"], MODULE.subprocess.STDOUT)

    def test_find_download_ignores_files_older_than_since(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            old = root / "old.pptx"
            new = root / "new.pptx"
            for path in (old, new):
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr(
                        "[Content_Types].xml",
                        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                        '<Override PartName="/ppt/presentation.xml" '
                        f'ContentType="{MODULE.PPTX_CONTENT_TYPE}"/></Types>',
                    )
                    archive.writestr("ppt/presentation.xml", "<p:presentation/>")

            older = time.time() - 60
            os.utime(old, (older, older))
            since = time.time() - 5
            found = MODULE.find_download([root], timeout=2.0, since=since)
            self.assertEqual(found.resolve(), new.resolve())

    def test_find_download_survives_files_vanishing_mid_scan(self):
        # Chrome renames "*.crdownload" files away between directory listing
        # and stat(); a vanished file must be skipped, not crash the export.
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            deck = root / "deck.pptx"
            with zipfile.ZipFile(deck, "w") as archive:
                archive.writestr(
                    "[Content_Types].xml",
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Override PartName="/ppt/presentation.xml" '
                    f'ContentType="{MODULE.PPTX_CONTENT_TYPE}"/></Types>',
                )
                archive.writestr("ppt/presentation.xml", "<p:presentation/>")
            ghost = root / "ghost.crdownload"
            ghost.write_bytes(b"partial download")

            real_stat = Path.stat
            seen = {"count": 0}

            def racy_stat(self, **kwargs):
                if self.name == "ghost.crdownload":
                    seen["count"] += 1
                    if seen["count"] > 1:
                        raise FileNotFoundError(2, "vanished mid-scan", str(self))
                return real_stat(self, **kwargs)

            with patch.object(Path, "stat", racy_stat):
                found = MODULE.find_download([root], timeout=2.0)
            self.assertEqual(found.resolve(), deck.resolve())

    def test_browser_open_does_not_pass_download_path(self):
        session = MODULE.BrowserSession(
            "/bin/agent-browser",
            "test-session",
            Path("."),
            Path("/tmp/downloads"),
        )
        with patch.object(session, "run") as run:
            session.open("http://127.0.0.1:9/?ndExport=1")
        run.assert_called_once_with(
            ["open", "http://127.0.0.1:9/?ndExport=1"],
            timeout=90,
        )

    def test_ensure_debug_chrome_is_windows_only(self):
        with patch.object(MODULE.sys, "platform", "linux"):
            self.assertIsNone(MODULE.ensure_debug_chrome())

    @patch.object(MODULE, "cdp_alive", return_value=True)
    def test_ensure_debug_chrome_prefers_working_explicit_port(self, cdp_alive):
        with patch.object(MODULE.sys, "platform", "win32"), \
                patch.dict(MODULE.os.environ, {"AGENT_BROWSER_CDP": "9444"}):
            self.assertEqual(MODULE.ensure_debug_chrome(), 9444)
        cdp_alive.assert_called_once_with(9444)

    def test_browser_session_exports_cdp_port_to_env(self):
        with patch.dict(MODULE.os.environ, {}, clear=False):
            MODULE.os.environ.pop("AGENT_BROWSER_CDP", None)
            with_port = MODULE.BrowserSession(
                "/bin/agent-browser", "s", Path("."), Path("/tmp/d"), cdp_port=9337
            )
            self.assertEqual(with_port.process_environment["AGENT_BROWSER_CDP"], "9337")
            without_port = MODULE.BrowserSession(
                "/bin/agent-browser", "s", Path("."), Path("/tmp/d")
            )
            self.assertNotIn("AGENT_BROWSER_CDP", without_port.process_environment)


if __name__ == "__main__":
    unittest.main()
