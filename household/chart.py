from household.models import FinancialYear, HouseholdClass, HouseholdService
from collections import OrderedDict
import json


def chart_data(audited, original, budgeted):
    """
    Get all the household bill totals for all avaliable years and join
    the data so that plotly can draw the graph.
    Eg: for 2015/16 we need all the total for all the income levels
    """
    data = {}
    household_class = HouseholdClass.objects.all().values("name")
    for h_class in household_class:
        data[h_class["name"]] = {"x": [], "y": []}

    for value in audited:
        data[value["household_class__name"]]["x"].append(
            value["financial_year__budget_year"]
        )
        data[value["household_class__name"]]["y"].append(str(value["total"]))

    for value in original:
        data[value["household_class__name"]]["x"].append(
            value["financial_year__budget_year"]
        )
        data[value["household_class__name"]]["y"].append(str(value["total"]))

    for value in budgeted:
        data[value["household_class__name"]]["x"].append(
            value["financial_year__budget_year"]
        )
        data[value["household_class__name"]]["y"].append(str(value["total"]))

    return data


def stack_chart(queryset):
    """
    function to format the household service totals data to present a stack chart
    """
    data = {}

    services = HouseholdService.objects.all().values("name")
    for s in services:
        data[s["name"]] = {"x": [], "y": []}
    for result in queryset:
        if result["total"]:
            data[result["service__name"]]["x"].append(
                result["financial_year__budget_year"]
            )
            data[result["service__name"]]["y"].append(str(result["total"]))
    data = OrderedDict(
        sorted(data.items(), key=lambda item: len(item[1]["x"]), reverse=True)
    )
    return json.dumps(data)


def percent_increase(queryset):
    """
    Calculate the percentage increase between the oldest financial year and the lastest financial year totals
    """
    increase_dict = {}
    classes = {results["household_class__name"]: {} for results in queryset}
    for k, v in classes.items():
        for results in queryset:
            if results["household_class__name"] == k:
                v[results["financial_year__budget_year"]] = results["total"]
    for k, v in classes.items():
        years = list(v.keys())
        years.sort()
        start_year = years[0]
        final_year = years[-1]

        if start_year:
            percent = ((v[final_year] - v[start_year]) / v[start_year]) * 100
            increase_dict[k] = round(percent, 2)

    increase_dict = {key.split(" ")[0]: values for key, values in increase_dict.items()}
    return increase_dict
