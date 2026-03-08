from etl.competitions_etl import run_competitions_etl


if __name__ == "__main__":
    result = run_competitions_etl()
    print(
        {
            "run_id": result.run_id,
            "status": result.status,
            "row_count": result.row_count,
            "error_message": result.error_message,
        }
    )
