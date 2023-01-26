export type DataNames = keyof typeof DATA_OPTIONS;

export const DATA_OPTIONS = {
  "US Census ACS 2021 Subset": {
    data: [
      "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/2021_5_yr_acs.csv",
      "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/zcta-centroids.csv",
    ],
    queries: [
      {
        query:
          "Which zip codes have the largest difference in population between genders?",
        sql: "SELECT tbl_0.zip_code, (tbl_0.male_pop - tbl_0.female_pop) AS gender_difference FROM tbl_0 ORDER BY gender_difference DESC;",
      },
      {
        query: "Which zip codes have the most old people and children?",
        sql: "SELECT tbl_0.zip_code, (tbl_0.elderly_pop + tbl_0.pop_under_5_years + tbl_0.pop_5_to_9_years + tbl_0.pop_10_to_14_years + tbl_0.pop_15_to_19_years) AS total_old_and_children FROM tbl_0 INNER JOIN tbl_1 ON tbl_0.zip_code = tbl_1.zcta ORDER BY total_old_and_children DESC;",
      },
      {
        query: "What is the current age distribution of the population?",
        sql: "SELECT SUM(tot_pop) AS 'Total Population', SUM(pop_under_5_years) AS 'Under 5 Years', SUM(pop_5_to_9_years) AS '5 to 9 Years', SUM(pop_10_to_14_years) AS '10 to 14 Years', SUM(pop_15_to_19_years) AS '15 to 19 Years', SUM(pop_20_to_24_years) AS '20 to 24 Years', SUM(pop_25_to_34_years) AS '25 to 34 Years', SUM(pop_35_to_44_years) AS '35 to 44 Years', SUM(pop_45_to_54_years) AS '45 to 54 Years', SUM(pop_55_to_59_years) AS '55 to 59 Years', SUM(pop_60_to_64_years) AS '60 to 64 Years', SUM(pop_65_to_74_years) AS '65 to 74 Years', SUM(pop_75_to_84_years) AS '75 to 84 Years', SUM(pop_85_years_and_over) AS '85 Years and Over' FROM tbl_0;",
      },
    ],
  },
  "Fortune 500": {
    data: [
      "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/fortune_500.csv",
    ],
    queries: [
      {
        query: "Which companies have over 100,000 employees?",
        sql: "SELECT name FROM tbl_0 WHERE employees > 100000;",
      },
      {
        query:
          "Which companies are within a 50 mile radius of Washington D.C.?",
        sql: "SELECT * FROM tbl_0 WHERE (3959 * acos(cos(radians(38.9072)) * cos(radians(latitude)) * cos(radians(longitude) - radians(-77.0369)) + sin(radians(38.9072)) * sin(radians(latitude)))) < 50;",
      },
      {
        query:
          "Which companies are not located within a 150 mile radius of any other company?",
        sql: "SELECT tbl_0.name FROM tbl_0 WHERE NOT EXISTS (SELECT * FROM tbl_0 tbl_1 WHERE tbl_0.name != tbl_1.name AND (6371 * acos(cos(radians(tbl_0.latitude)) * cos(radians(tbl_1.latitude)) * cos(radians(tbl_1.longitude) - radians(tbl_0.longitude)) + sin(radians(tbl_0.latitude)) * sin(radians(tbl_1.latitude)))) < 150);",
      },
    ],
  },
};
