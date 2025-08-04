import azure.functions as func

app = func.FunctionApp()

import update_schedules  # this triggers the decorator to register the function
