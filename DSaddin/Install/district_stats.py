import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import arcpy
import statistics
import csv


class DistrictStats:
    def __init__(self, shapefile):
        self.shapefile = shapefile

    def summary(self, field, dist_id=None):
        return Summary(self.shapefile, field, dist_id=dist_id)

    def csv(self, fields, outfile):
        with open(outfile, 'w') as output:
            wr = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
            wr.writerow(['General Summary'])
            wr.writerow(['Field', 'Mean', 'Median', 'St Dev'])
            for field in fields:
                s = self.summary(field)
                wr.writerow([field, s.mean(), s.median(), s.stdev()])
            for district in self.dist_ids():
                wr.writerow(['District ID ' + str(district)])
                wr.writerow(['Field', 'Mean', 'Median', 'St Dev'])
                for field in fields:
                    s = self.summary(field, dist_id=district)
                    wr.writerow([field, s.mean(), s.median(), s.stdev()])

    def dist_ids(self):
        districts = []
        rows = arcpy.SearchCursor(self.shapefile, fields="Dist_ID")
        for row in rows:
            instance = row.getValue("Dist_ID")
            districts.append(instance)
        value_set = set(districts)
        present_values = list(value_set)
        return present_values


class Summary:
    def __init__(self, shapefile, field, dist_id=None):
        self.shapefile = shapefile
        self.field = field
        self.values = []
        if dist_id is None:
            cursor = arcpy.SearchCursor(shapefile)
        else:
            cursor = arcpy.SearchCursor(shapefile,
                                        '"Dist_ID" = {0}'.format(dist_id))
        for row in cursor:
            try:
                if field == "Shape":
                    self.values.append(0.0)
                else:
                    value = str(row.getValue(field))
                    if value is None:
                        value = "0"
                    self.values.append(float(value))
            except ValueError:
                self.values.append(0.0)

    def mean(self):
        return statistics.mean(self.values)

    def median(self):
        return statistics.median(self.values)

    def stdev(self):
        return statistics.stdev(self.values)

# Example usage:
# ds = DistrictStats("C:/GIS/Project/tl_rd13_04_tract10.shp")
# print ds.summary("COUNTYFP10").stdev()
# ds.csv(["FID", "STATEFP10", "ALAND10"], "out.csv")
