# coding=utf-8

import javax.swing as swing
import java.awt as awt
from com.formdev.flatlaf.extras import FlatSVGIcon
from java.io import File

from emips.utils import SectorEnum
from emips.chem_spec import PollutantEnum
import os
import sys
import importlib
from mipylib import plotlib as plt


class EmissionPanel(swing.JPanel):

    def __init__(self, frm_main):
        super(EmissionPanel, self).__init__()

        self.frm_main = frm_main
        self.run_config = frm_main.run_config
        self.init_gui()
        if self.run_config is not None:
            self.update_run_configure(self.run_config)

    def init_gui(self):
        # Read emission script file
        label_read = swing.JLabel("Read module:")
        self.text_read = swing.JTextField("")        
        icon = FlatSVGIcon(File(os.path.join(self.frm_main.current_path, 'image', 'file-open.svg')))
        button_read = swing.JButton("", icon)
        button_read.actionPerformed = self.click_read_script

        # Sector choose
        label_sector = swing.JLabel("Sector:")
        self.combobox_sector = swing.JComboBox()
        for se in SectorEnum:
            self.combobox_sector.addItem(se)
        button_edit_sectors = swing.JButton("Edit sectors")

        # Pollutant choose
        label_pollutant = swing.JLabel("Pollutant:")
        self.combobox_pollutant = swing.JComboBox()
        for poll in PollutantEnum:
            self.combobox_pollutant.addItem(poll)
        button_edit_pollutants = swing.JButton("Edit pollutants")

        # Year and Month
        label_year = swing.JLabel("Year:")
        self.text_year = swing.JTextField("2017")
        label_month = swing.JLabel("Month:")
        self.combobox_month = swing.JComboBox()
        for m in range(1, 13):
            self.combobox_month.addItem(m)

        # Plot button
        button_plot = swing.JButton("Plot")
        button_plot.actionPerformed = self.click_plot

        # Layout
        layout = swing.GroupLayout(self)
        self.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addGroup(layout.createSequentialGroup()
                    .addComponent(label_read)
                    .addComponent(self.text_read)
                    .addComponent(button_read))
                .addGap(15)
                .addGroup(layout.createSequentialGroup()
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addComponent(label_sector)
                        .addComponent(label_pollutant)
                        .addComponent(label_year)
                        .addComponent(label_month))
                    .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.LEADING)
                        .addGroup(layout.createSequentialGroup()
                            .addComponent(self.combobox_sector)
                            .addComponent(button_edit_sectors))
                        .addGroup(layout.createSequentialGroup()
                            .addComponent(self.combobox_pollutant)
                            .addComponent(button_edit_pollutants))
                        .addComponent(self.text_year)
                        .addComponent(self.combobox_month)))
                .addGap(15)
                .addComponent(button_plot, swing.GroupLayout.Alignment.CENTER)
        )
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_read)
                    .addComponent(self.text_read)
                    .addComponent(button_read))
                .addGap(15)
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_sector)
                    .addComponent(self.combobox_sector)
                    .addComponent(button_edit_sectors))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_pollutant)
                    .addComponent(self.combobox_pollutant)
                    .addComponent(button_edit_pollutants))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_year)
                    .addComponent(self.text_year))
                .addGroup(layout.createParallelGroup(swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(label_month)
                    .addComponent(self.combobox_month))
                .addGap(15)
                .addComponent(button_plot)
        )

    def update_run_configure(self, run_config):
        """
        Update run configure.

        :param run_config: (*RunConfigure*) Run configure object.
        """
        self.run_config = run_config
        self.text_read.setText(self.run_config.emission_read_file)

    def click_read_script(self, e):
        """
        Read script button click event.
        """
        choose_file = swing.JFileChooser()
        ff = File(self.text_read.text)
        if ff.isFile():
            choose_file.setCurrentDirectory(ff.getParentFile())
        choose_file.setFileSelectionMode(swing.JFileChooser.FILES_ONLY)
        ret = choose_file.showOpenDialog(self)
        if ret == swing.JFileChooser.APPROVE_OPTION:
            ff = choose_file.getSelectedFile()
            self.text_read.text = ff.getAbsolutePath()
            self.run_config.emission_read_file = ff.getAbsolutePath()
            self.run_config.load_emission_module()

    def click_plot(self, e):
        """
        Plot button click event.
        """
        if self.run_config is None:
            return

        # Set cursor and progress bar
        self.setCursor(awt.Cursor(awt.Cursor.WAIT_CURSOR))
        self.frm_main.milab_app.getProgressBar().setVisible(True)

        # Read data
        sector = self.combobox_sector.getSelectedItem()
        pollutant = self.combobox_pollutant.getSelectedItem()
        year = int(self.text_year.text)
        month = self.combobox_month.getSelectedItem()
        emission = self.run_config.emission_module
        data = emission.read_emis(sector, pollutant, year, month)
        print(data)
        emis_grid = emission.get_emis_grid()
        lon = emis_grid.x_coord
        lat = emis_grid.y_coord

        # Plot
        plt.clf()
        plt.axesm()
        plt.geoshow('country', edgecolor='k')
        levs = [0.01, 0.1, 1, 5, 10, 15, 100]
        layer = plt.imshow(lon, lat, data * 1e2, levs)
        plt.colorbar(layer, shrink=0.8)
        plt.title('Emission - {} - {} - ({}-{})'.format(sector.name, pollutant.name, year, month))

        # Set cursor and progress bar
        self.setCursor(awt.Cursor(awt.Cursor.DEFAULT_CURSOR))
        self.frm_main.milab_app.getProgressBar().setVisible(False)
