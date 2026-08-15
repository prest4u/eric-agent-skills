#!/usr/bin/env python3
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

SPEC = importlib.util.spec_from_file_location("export_images", SCRIPTS_DIR / "export_images.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def make_images_zip(path: Path, names=("1.jpeg", "10.jpeg", "2.jpeg")) -> None:
    # 1x1 white JPEG, the smallest valid payload Pillow can open.
    import base64

    pixel = base64.b64decode(
        "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////"
        "////////////////////////////////////////////2wBDAf//////////////////"
        "////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB"
        "/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMB"
        "AAIQAxAAAAGf/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABBQJ//8QAFBEBAAAA"
        "AAAAAAAAAAAAAAAAAP/aAAgBAwEBPwF//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgB"
        "AgEBPwF//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQAGPwJ//8QAFBABAAAAAAAA"
        "AAAAAAAAAAAAAP/aAAgBAQABPyF//9oADAMBAAIAAwAAABCf/8QAFBEBAAAAAAAAAAAA"
        "AAAAAAAAAP/aAAgBAwEPEBB//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAgEPEBB/"
        "/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxB//9k="
    )
    with zipfile.ZipFile(path, "w") as archive:
        for name in names:
            archive.writestr(name, pixel)


class ExportImagesTests(unittest.TestCase):
    def test_image_output_uses_same_project_boundary(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            project = root / "project"
            project.mkdir()
            manifest = project / "deck.pptd"
            manifest.touch()
            target = MODULE.resolve_output_target(
                manifest, project / ".qa-images", kind="directory"
            )
            self.assertEqual(target, (project / ".qa-images").resolve())
            with self.assertRaises(MODULE.ExportError):
                MODULE.resolve_output_target(
                    manifest, root / "qa-images", kind="directory"
                )

    def test_force_refuses_unowned_project_directory(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            assets = project / "assets"
            assets.mkdir()
            source = assets / "source.png"
            source.write_bytes(b"keep")

            with self.assertRaisesRegex(MODULE.OutputSafetyError, "unowned directory"):
                MODULE.ensure_image_output_replaceable(
                    assets, manifest, force=True
                )
            self.assertEqual(source.read_bytes(), b"keep")

    def test_owned_image_output_can_be_replaced_transactionally(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            output = project / ".qa-images"
            output.mkdir()
            (output / "old.txt").write_text("old", encoding="utf-8")
            (output / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )
            staged = project / ".qa-images.staged"
            staged.mkdir()
            (staged / "new.txt").write_text("new", encoding="utf-8")
            (staged / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )

            MODULE.commit_image_output(
                staged, output, manifest, force=True
            )
            self.assertFalse((output / "old.txt").exists())
            self.assertEqual((output / "new.txt").read_text(encoding="utf-8"), "new")
            self.assertFalse(staged.exists())
            backups = [path for path in project.iterdir() if path.name.endswith(".backup")]
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / "old.txt").read_text(encoding="utf-8"), "old")

    def test_no_force_commit_preserves_directory_that_appeared(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            output = project / ".qa-images"
            staged = project / ".qa-images.staged"
            staged.mkdir()
            (staged / "new.txt").write_text("new", encoding="utf-8")
            (staged / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )

            output.mkdir()
            competitor = output / "user.txt"
            competitor.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.ExportError, "already exists"):
                MODULE.commit_image_output(
                    staged, output, manifest, force=False
                )
            self.assertEqual(competitor.read_text(encoding="utf-8"), "keep")
            self.assertEqual((staged / "new.txt").read_text(encoding="utf-8"), "new")

    def test_force_rejects_directory_replaced_during_marker_validation(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            output = project / ".qa-images"
            output.mkdir()
            (output / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )
            (output / "old.txt").write_text("old", encoding="utf-8")
            staged = project / ".qa-images.staged"
            staged.mkdir()
            (staged / "new.txt").write_text("new", encoding="utf-8")
            (staged / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )

            def replace_after_marker(_output, _manifest):
                MODULE.shutil.rmtree(output)
                output.mkdir()
                (output / "concurrent-user.txt").write_text("keep", encoding="utf-8")
                return True

            with patch.object(
                MODULE,
                "image_output_is_owned",
                side_effect=replace_after_marker,
            ):
                with self.assertRaisesRegex(MODULE.OutputSafetyError, "identity changed"):
                    MODULE.commit_image_output(
                        staged, output, manifest, force=True
                    )
            self.assertEqual(
                (output / "concurrent-user.txt").read_text(encoding="utf-8"),
                "keep",
            )
            self.assertEqual((staged / "new.txt").read_text(encoding="utf-8"), "new")

    def test_force_preserves_same_directory_concurrent_addition_after_validation(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            output = project / ".qa-images"
            output.mkdir()
            (output / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )
            (output / "old.txt").write_text("old", encoding="utf-8")
            staged = project / ".qa-images.staged"
            staged.mkdir()
            (staged / "new.txt").write_text("new", encoding="utf-8")
            (staged / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )

            real_guard = MODULE.guarded_image_output_identity
            calls = 0

            @MODULE.contextmanager
            def add_after_validation(_output, _manifest, *, force):
                nonlocal calls
                with real_guard(_output, _manifest, force=force) as guard:
                    calls += 1
                    if calls == 2:
                        (_output / "concurrent-user.txt").write_text(
                            "keep",
                            encoding="utf-8",
                        )
                    yield guard

            with patch.object(
                MODULE,
                "guarded_image_output_identity",
                side_effect=add_after_validation,
            ):
                with self.assertRaisesRegex(
                    MODULE.OutputSafetyError,
                    "contents changed",
                ):
                    MODULE.commit_image_output(
                        staged,
                        output,
                        manifest,
                        force=True,
                    )
            self.assertEqual(
                (output / "concurrent-user.txt").read_text(encoding="utf-8"),
                "keep",
            )
            self.assertEqual((output / "old.txt").read_text(encoding="utf-8"), "old")
            self.assertEqual((staged / "new.txt").read_text(encoding="utf-8"), "new")

    def test_force_preserves_backup_changed_after_rename(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            output = project / ".qa-images"
            output.mkdir()
            (output / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )
            (output / "old.txt").write_text("old", encoding="utf-8")
            staged = project / ".qa-images.staged"
            staged.mkdir()
            (staged / "new.txt").write_text("new", encoding="utf-8")
            (staged / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )

            real_snapshot = MODULE.image_output_tree_snapshot
            injected = False

            def add_after_backup_snapshot(path):
                nonlocal injected
                snapshot = real_snapshot(path)
                if path.name.endswith(".backup") and not injected:
                    (path / "concurrent-user.txt").write_text("keep", encoding="utf-8")
                    injected = True
                return snapshot

            with patch.object(
                MODULE,
                "image_output_tree_snapshot",
                side_effect=add_after_backup_snapshot,
            ):
                with self.assertRaisesRegex(
                    MODULE.OutputSafetyError,
                    "backup contents changed",
                ):
                    MODULE.commit_image_output(
                        staged,
                        output,
                        manifest,
                        force=True,
                    )
            backups = [path for path in project.iterdir() if path.name.endswith(".backup")]
            self.assertEqual(len(backups), 1)
            self.assertEqual(
                (backups[0] / "concurrent-user.txt").read_text(encoding="utf-8"),
                "keep",
            )
            self.assertEqual((backups[0] / "old.txt").read_text(encoding="utf-8"), "old")
            self.assertEqual((output / "new.txt").read_text(encoding="utf-8"), "new")

    def test_force_preserves_write_after_final_snapshot_returns(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            manifest = project / "deck.pptd"
            manifest.touch()
            output = project / ".qa-images"
            output.mkdir()
            (output / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )
            (output / "old.txt").write_text("old", encoding="utf-8")
            staged = project / ".qa-images.staged"
            staged.mkdir()
            (staged / "new.txt").write_text("new", encoding="utf-8")
            (staged / MODULE.IMAGE_OUTPUT_MARKER).write_text(
                MODULE.json.dumps(MODULE.expected_image_output_marker(manifest)),
                encoding="utf-8",
            )

            real_snapshot = MODULE.image_output_tree_snapshot
            backup_snapshot_calls = 0

            def add_after_final_snapshot(path):
                nonlocal backup_snapshot_calls
                snapshot = real_snapshot(path)
                if path.name.endswith(".backup"):
                    backup_snapshot_calls += 1
                    if backup_snapshot_calls == 2:
                        (path / "concurrent-user.txt").write_text(
                            "keep",
                            encoding="utf-8",
                        )
                return snapshot

            with patch.object(
                MODULE,
                "image_output_tree_snapshot",
                side_effect=add_after_final_snapshot,
            ):
                MODULE.commit_image_output(
                    staged,
                    output,
                    manifest,
                    force=True,
                )
            backups = [path for path in project.iterdir() if path.name.endswith(".backup")]
            self.assertEqual(backup_snapshot_calls, 2)
            self.assertEqual(len(backups), 1)
            self.assertEqual(
                (backups[0] / "concurrent-user.txt").read_text(encoding="utf-8"),
                "keep",
            )
            self.assertEqual((backups[0] / "old.txt").read_text(encoding="utf-8"), "old")
            self.assertEqual((output / "new.txt").read_text(encoding="utf-8"), "new")

    def test_page_sort_key_orders_numeric_stems(self):
        paths = [Path("10.jpeg"), Path("2.jpeg"), Path("cover.jpeg"), Path("1.jpeg")]
        ordered = sorted(paths, key=MODULE.page_sort_key)
        self.assertEqual(
            [path.name for path in ordered],
            ["1.jpeg", "2.jpeg", "10.jpeg", "cover.jpeg"],
        )

    def test_is_image_zip_accepts_image_entries_only(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            good = root / "images.zip"
            make_images_zip(good)
            self.assertTrue(MODULE.is_image_zip(good))

            bad = root / "text.zip"
            with zipfile.ZipFile(bad, "w") as archive:
                archive.writestr("readme.txt", "hello")
            self.assertFalse(MODULE.is_image_zip(bad))
            self.assertFalse(MODULE.is_image_zip(root / "missing.zip"))

    def test_unzip_images_flattens_and_sorts(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            archive_path = root / "images.zip"
            make_images_zip(archive_path, names=("1.jpeg", "10.jpeg", "2.jpeg", "note.txt"))
            images = MODULE.unzip_images(archive_path, root / "pages")
            self.assertEqual(
                [path.name for path in images], ["1.jpeg", "2.jpeg", "10.jpeg"]
            )

    def test_stitch_overview_grid(self):
        try:
            image_cls, draw_cls, image_font = MODULE.ensure_pillow()
        except MODULE.ExportError:
            self.skipTest("Pillow is not available")
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            images = []
            for index in range(1, 5):
                path = root / f"{index}.jpeg"
                image = image_cls.new("RGB", (320, 180), (index * 40 % 255, 30, 60))
                image.save(path, "JPEG")
                images.append(path)
            overview = MODULE.stitch_overview(
                images, root / "overview.jpg", image_cls, draw_cls, image_font
            )
            self.assertTrue(overview.is_file())
            with image_cls.open(overview) as result:
                self.assertEqual(
                    result.width,
                    3 * MODULE.OVERVIEW_THUMB_WIDTH + 4 * MODULE.OVERVIEW_GAP,
                )
                rows = 2
                cell = MODULE.OVERVIEW_LABEL_HEIGHT + 360
                self.assertEqual(result.height, rows * cell + (rows + 1) * MODULE.OVERVIEW_GAP)


if __name__ == "__main__":
    unittest.main()
