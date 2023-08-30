resource "aws_timestreamwrite_database" "db_sensor_database" {
  database_name = "db_sensor"

  tags = {
    project = "master"
  }
}


resource "aws_timestreamwrite_table" "temp_evolution_table" {
  database_name = aws_timestreamwrite_database.db_sensor_database.database_name
  table_name    = "temp_evolution"

  retention_properties {
    magnetic_store_retention_period_in_days = 1
    memory_store_retention_period_in_hours  = 1
  }

  tags = {
    project = "master"
  }
}