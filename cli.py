#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from scripts.db_loader import upload_project as up


@click.command()
@click.option('--matrix-stats', type=click.Path(exists=True),
              help='Combo Matrix Statistics File (CSV format)',
              prompt='Matrix Stats File')
@click.option('--well-stats', help='Combo Well Statistics File (CSV format)',
              type=click.Path(exists=True), prompt='Matrix Stats File')
@click.option('--nlme-stats', help='NLME Stats File (CSV format)',
              type=click.Path(exists=True), prompt='Matrix Stats File')
@click.option('--name', '--project-name', prompt='Project Name',
              help='Project Name', required=True)
def upload_project(matrix_stats, well_stats, nlme_stats, project_name):
    """Upload a project"""
    up(combo_matrix_stats_path=matrix_stats, combo_well_stats_path=well_stats,
       nlme_stats_path=nlme_stats, project_name=project_name)


if __name__ == '__main__':
    upload_project()