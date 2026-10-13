from sqlalchemy import create_engine

def get_engine():
    engine = create_engine(
        'mssql+pyodbc://localhost/Tennis?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes'
    )
    return engine

