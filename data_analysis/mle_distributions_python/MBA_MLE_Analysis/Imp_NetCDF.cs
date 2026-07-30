using MBA;
using Microsoft.Research.ScientificDataSet.NetCDF;
using System;
using System.Collections.Generic;

namespace MBA_MLE_Analysis
{
    class Imp_NetCDF
    {
        private static int ncid;

        public static bool Import(Track p_Track)
        {
            double[] X, Y, Z;
            float[] Latitude, Longitude, Altitude;
            DateTime[] DateTimes;
            List<TStep> TSteps = new List<TStep>();

            // Open the file
            if (!DotNetCDF_MBA.OpenTAFile(Track.Filename, out ncid, out int TotPoints)) return false;

            // Create the array of Track points
            DateTimes = DotNetCDF_MBA.GetDates(ncid);

            // Read each of the variables and convert
            Track.LatLonData = DotNetCDF_MBA.VarExists(ncid, "Latitude");
            Track.AltData = DotNetCDF_MBA.VarExists(ncid, "Altitude");
            Track.ZData = DotNetCDF_MBA.VarExists(ncid, "Z") || DotNetCDF_MBA.VarExists(ncid, "Depth");

            X = new double[1];
            Y = new double[1];
            Z = new double[1];
            Latitude = new float[1];
            Longitude = new float[1];
            Altitude = new float[1];

            // Update either X, Y, Z or Lat & Long, see which we have
            if (Track.LatLonData)
            {
                Latitude = new float[TotPoints];
                Longitude = new float[TotPoints];
                DotNetCDF_MBA.Get_float(ncid, "Latitude", Latitude);
                DotNetCDF_MBA.Get_float(ncid, "Longitude", Longitude);
            }
            else
            {
                X = new double[TotPoints];
                Y = new double[TotPoints];
                DotNetCDF_MBA.Get_double(ncid, "X", X);
                DotNetCDF_MBA.Get_double(ncid, "Y", Y);
            }

            // Get Z or Altitude
            if (Track.AltData)
            {
                Altitude = new float[TotPoints];
                DotNetCDF_MBA.Get_float(ncid, "Altitude", Altitude);
            }
            else if (Track.ZData)
            {
                Z = new double[TotPoints];

                if (DotNetCDF_MBA.VarExists(ncid, "Z")) DotNetCDF_MBA.Get_double(ncid, "Z", Z);
                else DotNetCDF_MBA.Get_double(ncid, "Depth", Z);
            }

            DotNetCDF_MBA.CloseFile(ncid);

            // Read the imported data and add points to the track
            for (int i = 0; i < DateTimes.Length; i++)
            {
                // Add points with Lat, Long and Altitude data - note that altitude is negated
                if (Track.LatLonData && Track.ZData) TSteps.Add(new TStep(DateTimes[i], Latitude[i], Longitude[i], -Z[i]));
                else if (Track.LatLonData && Track.AltData) TSteps.Add(new TStep(DateTimes[i], Latitude[i], Longitude[i], -Altitude[i]));

                // Add points with Lat, Long data
                else if (Track.LatLonData) TSteps.Add(new TStep(DateTimes[i], Latitude[i], Longitude[i], 0.0));

                // Add points with X, Y, Z data
                else if (Track.ZData) TSteps.Add(new TStep(DateTimes[i], X[i], Y[i], -Z[i]));

                // Or just add X & Y
                else TSteps.Add(new TStep(DateTimes[i], X[i], Y[i], 0.0));
            }

            // If all's well add the points
            p_Track.AddPoints(TSteps);

            return true;
        }
    }
}
