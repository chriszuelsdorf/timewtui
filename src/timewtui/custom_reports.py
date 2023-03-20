import json
import datetime
from dateutil import tz
import pandas as pd

DTF = "%Y%m%dT%H%M%SZ"
from_zone = tz.tzutc()
to_zone = tz.tzlocal()


class CustomReport:
    def __init__(self, json_string: str) -> None:
        self.di = json.loads(json_string)
        self.report_time = datetime.datetime.now()

    def getout(self) -> list:
        raise NotImplementedError()

    def convertdf(self, to_tz, exclude_older=None):
        self.df = pd.DataFrame(self.di)
        self.df["ntags"] = self.df["tags"].apply(len)
        self.df = self.df.explode("tags")
        self.log(self.df.loc[:, "end"], 8)
        self.df.loc[:, ["start", "end"]] = self.df.loc[
            :, ["start", "end"]
        ].applymap(
            lambda x: self.report_time.replace(tzinfo=to_zone)
            if isinstance(x, float)
            else datetime.datetime.strptime(x, DTF)
            .replace(tzinfo=from_zone)
            .astimezone(to_tz)
        )
        if exclude_older is not None:
            self.df = self.df[
                self.df["start"] > exclude_older.replace(tzinfo=to_zone)
            ]
        self.df["dur"] = self.df["end"] - self.df["start"]


class SumN(CustomReport):
    def getout(self, n, logger, multitag_time_div=True, to_tz=to_zone):
        self.log = logger
        self.convertdf(
            to_tz,
            exclude_older=datetime.datetime.now() - datetime.timedelta(days=n),
        )

        if multitag_time_div:
            self.df["dur"] = self.df["dur"] / self.df["ntags"]

        def ctagg(series):
            s = series.apply(lambda x: x.total_seconds()).sum()
            h = int(s // 3600)
            m = int((s - (3600 * h)) // 60)
            return f"{h}h{m}m"

        self.df["pct"] = 100 * self.df["dur"] / self.df["dur"].sum()
        agged = self.df.groupby("tags").agg(
            {"dur": ctagg, "pct": lambda x: f"{sum(x):5.2f}%"}
        )
        markdown_string = (
            agged.reset_index()
            .rename(
                columns={
                    "tags": "Tag",
                    "dur": "Duration",
                    "pct": "Percent of Time",
                }
            )
            .to_markdown(tablefmt="simple", index=False)
        )
        return [
            x for x in markdown_string.split("\n") if not x.strip("- ") == ""
        ]
