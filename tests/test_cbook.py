#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pyxray.cbook import ProgressMixin, ProgressReportMixin

# Globals and constants variables.

class MockProgress(ProgressMixin):
    pass

class MockProgressReport(ProgressReportMixin):
    pass

@pytest.fixture
def progress():
    return MockProgress()

def test_progress_update(progress):
    progress.update(50)
    assert progress.progress == 50

@pytest.fixture
def progress_report(progress):
    report = MockProgressReport()
    report.add_reporthook(lambda p: progress.update(p))
    return report

def test_progress_report_update(progress_report, progress):
    assert progress.progress == 0

    progress_report.update(50)

    assert progress_report.progress == 50
    assert progress.progress == 50

