# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from mpdg.govbr.observatorio.testing import MPDG_GOVBR_OBSERVATORIO_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that mpdg.govbr.observatorio is properly installed."""

    layer = MPDG_GOVBR_OBSERVATORIO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mpdg.govbr.observatorio is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'mpdg.govbr.observatorio'))

    def test_browserlayer(self):
        """Test that IMpdgGovbrObservatorioLayer is registered."""
        from mpdg.govbr.observatorio.interfaces import (
            IMpdgGovbrObservatorioLayer)
        from plone.browserlayer import utils
        self.assertIn(IMpdgGovbrObservatorioLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MPDG_GOVBR_OBSERVATORIO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['mpdg.govbr.observatorio'])

    def test_product_uninstalled(self):
        """Test if mpdg.govbr.observatorio is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'mpdg.govbr.observatorio'))

    def test_browserlayer_removed(self):
        """Test that IMpdgGovbrObservatorioLayer is removed."""
        from mpdg.govbr.observatorio.interfaces import \
            IMpdgGovbrObservatorioLayer
        from plone.browserlayer import utils
        self.assertNotIn(IMpdgGovbrObservatorioLayer, utils.registered_layers())
