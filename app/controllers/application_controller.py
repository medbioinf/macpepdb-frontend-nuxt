import io

from sqlalchemy.orm import sessionmaker
from flask import render_template
import matplotlib
import matplotlib.pyplot as plt

from macpepdb.tasks.statistics import Statistics

from app import app, macpepdb_session, config

class ApplicationController:
    pass

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

        return render_template(
            'application/dashboard.j2',
            peptide_partitions_svg = peptide_partitions_svg,
            peptide_count = peptide_count,
            partition_boundaries = partition_boundaries
        )
