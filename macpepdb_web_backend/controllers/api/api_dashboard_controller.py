
import io
import datetime
import matplotlib.pyplot as plt

from flask import jsonify
from macpepdb.models.maintenance_information import MaintenanceInformation
from macpepdb.proteomics.mass.convert import to_float as mass_to_float
from macpepdb.tasks.statistics import Statistics

from macpepdb_web_backend import app, get_database_connection
from macpepdb_web_backend.controllers.application_controller import ApplicationController

class ApiDashboardController(ApplicationController):
    @staticmethod
    @app.route("/api/dashboard")
    def show():
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:

            peptide_count, peptide_partitions_svg = ApiDashboardController.get_peptide_infos(database_cursor)
            partition_boundaries = [[boundary[0], mass_to_float(boundary[1]), mass_to_float(boundary[2])] for boundary in Statistics.get_partition_boundaries(database_cursor)]
            digestion_paramters = MaintenanceInformation.select(database_cursor, MaintenanceInformation.DIGESTION_PARAMTERS_KEY)
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

            database_status = MaintenanceInformation.select(database_cursor, MaintenanceInformation.DATABASE_STATUS_KEY)
            if database_status:
                database_status = database_status.values
                database_status['maintenance_mode'] = "On (updating)" if database_status['maintenance_mode'] else 'Off'
                database_status['last_update'] = datetime.datetime.utcfromtimestamp(database_status['last_update']).isoformat(sep=' ', timespec='minutes')
            else:
                database_status = {
                    'maintenance_mode': 'n/a',
                    'last_update': 'n/a'
                }

            database_comment = MaintenanceInformation.select(database_cursor, MaintenanceInformation.COMMENT_KEY)
            if database_comment:
                database_comment = database_comment.values["text"]

        return jsonify({
            "peptide_partitions_svg": peptide_partitions_svg,
            "peptide_count": peptide_count,
            "partition_boundaries": partition_boundaries,
            "digestion_paramters": digestion_paramters,
            "database_status": database_status,
            "database_comment": database_comment
        })

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
    def get_peptide_infos(database_cursor) -> tuple:
        partition_utilization_estimations = Statistics.estimate_peptide_partition_utilizations(database_cursor)
        return ApiDashboardController.create_sum_and_diagram_for_partition_utilizations(partition_utilization_estimations, 'peptides')