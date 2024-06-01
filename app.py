from shiny import App, ui, render, reactive
import pandas as pd
from datetime import date, datetime, timedelta
import time

# Function to calculate working days between two dates
def calculate_working_days(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    total_working_days = len(date_range)
    return total_working_days

# UI
app_ui = ui.page_fluid(
    ui.panel_title("Contrato de Duração Determinada - CDD"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_date("start_date", "Data de Início do Contrato", value=date(2023, 3, 22)),
            ui.input_date("end_date", "Data de Término do Contrato", value=date(2029, 3, 22)),
            ui.input_action_button("start_timer", "Start Countdown")
        ),
        ui.panel_main(
            ui.output_table("data_table"),
            ui.output_ui("countdown_timer")
        )
    )
)

# Server
def server(input, output, session):

    # Reactive values to store the countdown state
    countdown = reactive.Value(0)
    remaining_days = reactive.Value(0)
    remaining_hours = reactive.Value(0)

    @reactive.event(input.start_timer)
    def start_countdown():
        total_working_days = calculate_working_days(input.start_date(), input.end_date())
        worked_days = calculate_working_days(input.start_date(), date.today())
        remaining_days.set(total_working_days - worked_days)
        remaining_hours.set((total_working_days - worked_days) * 8)

        # Start countdown
        countdown.set(remaining_hours() * 3600)

    @reactive.Effect
    @reactive.event(countdown)
    def update_countdown():
        if countdown() > 0:
            time.sleep(1)
            countdown.set(countdown() - 1)

    @output
    @render.table
    def data_table():
        total_working_days = calculate_working_days(input.start_date(), input.end_date())
        worked_days = calculate_working_days(input.start_date(), date.today())
        remaining_days_val = total_working_days - worked_days
        remaining_hours_val = remaining_days_val * 8

        data = {
            'Categoria': ['Duracao', 'Dias Trabalhados', 'Dias Restantes'],
            'Dias': [total_working_days, worked_days, remaining_days_val],
            'Meses': [round(total_working_days / 30.44, 2), round(worked_days / 30.44, 2), round(remaining_days_val / 30.44, 2)],
            'Horas': [total_working_days * 8, worked_days * 8, remaining_hours_val]
        }

        df = pd.DataFrame(data)
        return df

    @output
    @render.ui
    def countdown_timer():
        total_seconds = countdown()
        days = remaining_days()
        hours, rem = divmod(total_seconds, 3600)
        mins, secs = divmod(rem, 60)

        return ui.TagList(
            ui.div(
                style="display: flex; justify-content: center; align-items: center; font-size: 36px; font-weight: bold;",
                ui.div(
                    style="text-align: center; margin: 0 10px;",
                    ui.div(style="font-size: 24px;", "DAYS"),
                    ui.div(f"{days:02d}")
                ),
                ui.div(
                    style="text-align: center; margin: 0 10px;",
                    ui.div(style="font-size: 24px;", "HOURS"),
                    ui.div(f"{hours:02d}")
                ),
                ui.div(
                    style="text-align: center; margin: 0 10px;",
                    ui.div(style="font-size: 24px;", "MINUTES"),
                    ui.div(f"{mins:02d}")
                ),
                ui.div(
                    style="text-align: center; margin: 0 10px;",
                    ui.div(style="font-size: 24px;", "SECONDS"),
                    ui.div(f"{secs:02d}")
                )
            )
        )

app = App(app_ui, server)

