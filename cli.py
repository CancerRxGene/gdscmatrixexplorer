#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from scripts.db_loader import upload_project as up
from scripts.delete_project import delete_project as dp
from scripts.upload_anchor import upload_anchor

@click.group()
def manage():
    pass

@manage.command()
@click.option('--matrix-stats', type=click.Path(exists=True),
              help='Combo Matrix Statistics File (CSV format)',
              prompt='Matrix Stats File')
@click.option('--well-stats', help='Combo Well Statistics File (CSV format)',
              type=click.Path(exists=True), prompt='Well Stats File')
@click.option('--nlme-stats', help='NLME Stats File (CSV format)',
              type=click.Path(exists=True), prompt='NLME Stats File')
@click.option('--name', '--project-name', prompt='Project Name',
              help='Project Name', required=True)
def upload_project(matrix_stats, well_stats, nlme_stats, project_name):
    """Upload a project"""
    up(combo_matrix_stats_path=matrix_stats, combo_well_stats_path=well_stats,
       nlme_stats_path=nlme_stats, project_name=project_name)


@manage.command()
@click.option('--name', '--project-name', prompt='Project Name',
              help='Project Name', required=True)
def delete_project(project_name):
    """Delete a project"""

    dp(name=project_name)

@manage.command()
@click.option('--name','--project-name', prompt='Project Name', help='Project Name', required=True)
@click.option('--anchor_combi', type=click.Path(exists=True),
              help='Anchor Combi File (CSV format)',
              prompt='Anchor Combi File')
def upload_anchor_project(project_name, anchor_combi):
    upload_anchor(anchor_result_path=anchor_combi, project_name=project_name)

if __name__ == '__main__':
    manage()