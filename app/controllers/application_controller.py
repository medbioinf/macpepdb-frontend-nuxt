import datetime
import io

from sqlalchemy.orm import sessionmaker
from flask import render_template
import matplotlib
import matplotlib.pyplot as plt

from macpepdb.models.maintenance_information import MaintenanceInformation
from macpepdb.tasks.statistics import Statistics

from app import app, macpepdb_session, config

class ApplicationController:
    @staticmethod
    @app.errorhandler(404)
    def recourse_not_found(error):
        return render_template("application/404.j2"), 404

    @staticmethod
    def create_sum_and_diagram_for_partition_utilizations(partition_utilization_estimations: list, ylabel: str) -> tuple:
        sum = 0
        for estimation in partition_utilization_estimations:
            sum += estimation[1]
        # Create diagram
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, xlabel='partition', ylabel=ylabel)
        ax.bar(
            [idx for idx in range(len(partition_utilization_estimations))],
            [estimation[1] for estimation in partition_utilization_estimations]
        )
        buffer = io.StringIO()
        fig.savefig(buffer, format='svg')
        return sum, buffer.getvalue()

    @staticmethod
    def get_peptide_infos(session) -> tuple:
        partition_utilization_estimations = Statistics.estimate_peptide_partition_utilizations(session)
        return ApplicationController.create_sum_and_diagram_for_partition_utilizations(partition_utilization_estimations, 'peptides')

    @staticmethod
    @app.route("/", endpoint="root_path")
    def dashboard():
        peptide_count, peptide_partitions_svg = ApplicationController.get_peptide_infos(macpepdb_session)
        partition_boundaries = Statistics.get_partition_boundaries(macpepdb_session)
        digestion_paramters = macpepdb_session.query(MaintenanceInformation).filter(MaintenanceInformation.key == MaintenanceInformation.DIGESTION_PARAMTERS_KEY).one_or_none()
        if digestion_paramters:
            digestion_paramters = digestion_paramters.values
            digestion_paramters['enzyme_name'] = digestion_paramters['enzyme_name'][0].upper() + digestion_paramters['enzyme_name'][1:].lower()
        else:
            digestion_paramters = {
                'enzyme_name': 'n/a',
                'maximum_number_of_missed_cleavages': 'n/a',
                'minimum_peptide_length': 'n/a',
                'maximum_peptide_length': 'n/a'
            }

        database_status = macpepdb_session.query(MaintenanceInformation).filter(MaintenanceInformation.key == MaintenanceInformation.DATABASE_STATUS_KEY).one_or_none()
        if database_status:
            database_status = database_status.values
            database_status['maintenance_mode'] = "On (updating)" if database_status['maintenance_mode'] else 'Off'
            database_status['last_update'] = datetime.datetime.utcfromtimestamp(database_status['last_update']).isoformat(sep=' ', timespec='minutes')
        else:
            database_status = {
                'maintenance_mode': 'n/a',
                'last_update': 'n/a'
            }

        return render_template(
            'application/dashboard.j2',
            peptide_partitions_svg = peptide_partitions_svg,
            peptide_count = peptide_count,
            partition_boundaries = partition_boundaries,
            digestion_paramters = digestion_paramters,
            database_status = database_status
        )
