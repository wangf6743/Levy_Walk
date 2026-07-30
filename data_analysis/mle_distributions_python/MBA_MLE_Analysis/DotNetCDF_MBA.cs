using Microsoft.Research.ScientificDataSet.NetCDF;
using System;
using System.IO;
using System.Text;
using System.Windows.Forms;

namespace MBA
{
    class DotNetCDF_MBA
    {
         public static bool NetCDF_OK = false;

        // Open a DA file
        public static bool OpenDAFile(string p_FileName, out int ncid, out int TotPoints)
        {
            if (!OpenFile(p_FileName, out ncid, out TotPoints)) return false;

            // Check it is a track data file or an MBA NetCDF file
            if (CheckMBADAFormat(ncid)) return true;

            MessageBox.Show("File is not a recognised MBA DA NetCDF file", "NetCDF Import error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return false;
        }

        // Open a TA file
        public static bool OpenTAFile(string p_FileName, out int ncid, out int TotPoints)
        {
            if (!OpenFile(p_FileName, out ncid, out TotPoints)) return false;

            // Check it is a track data file or an MBA NetCDF file
            if (CheckMBATAFormat(ncid)) return true;

            MessageBox.Show("File is not a recognised MBA TA NetCDF file", "NetCDF Import error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return false;
        }

        // Open a file for output
        public static bool OpenOutputFile(string p_FileName, out int ncid)
        {
            int status;
            ncid = 0;

            // try and open the file
            try
            {
                status = NetCDF.nc_create(p_FileName, NetCDF.CreateMode.NC_NETCDF4, out ncid);
            }
            catch (Exception e)
            {
                MessageBox.Show("Error when calling NetCDF open function."
                                + "\nError is : " + e.Message,
                                "NetCDF error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }

            if (status != 0)
            {
                MessageBox.Show("Error when opening a NetCDF file.\nstatus = "+ status.ToString(),
                                "NetCDF error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }

            return true;
        }

        // Open a file to read
        public static bool OpenFile(string p_FileName, out int ncid, out int TotPoints)
        {
            int status;
            ncid = TotPoints = 0;

            // Check for the netcdf4.dll file and copy it if we can
            if (!CheckNetCDF()) return false;

            // try and open the file
            try
            {
                status = NetCDF.nc_open(p_FileName, NetCDF.CreateMode.NC_NOWRITE, out ncid);
            }
            catch (Exception e)
            {
                MessageBox.Show("Error when calling NetCDF open function."
                                + "\nError is : " + e.Message,
                                "NetCDF error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }

            if (status != 0)
            {
                MessageBox.Show("Error when opening a NetCDF file.\nstatus = " + status.ToString(),
                                "NetCDF error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }

            // Get the length of the DateTime dimension - the number of points in the file
            NetCDF.nc_inq_dimlen(ncid, 0, out TotPoints);

            return true;
        }

        public static bool CheckMBADAFormat(int ncid)
        {
            // If it has the old format ID then it's OK
            if (GetGlobalAttribute(ncid, "MBA_Dive_Analysis_Version").Length > 0) return true;

            // If it's the new more general format then check we have what we need
            if (GetGlobalAttribute(ncid, "MBA_NetCDF").Length == 0) return false;

            // Check we have depth
            if (NetCDF.nc_inq_varid(ncid, "Depth", out int varid) == 0) return true;

            return false;
        }

        public static bool CheckMBATAFormat(int ncid)
        {
            int varid;

            // If it has the old format ID then it's OK
            if (GetGlobalAttribute(ncid, "MBA_Track_Analysis_Version").Length > 0) return true;

            // If it's the new more general format then check we have what we need
            if (GetGlobalAttribute(ncid, "MBA_NetCDF").Length == 0) return false;

            // Check we have X & Y or Latitude and Longitude
            if (NetCDF.nc_inq_varid(ncid, "X", out varid) == 0 && NetCDF.nc_inq_varid(ncid, "Y", out varid) == 0) return true;
            if (NetCDF.nc_inq_varid(ncid, "Latitude", out varid) == 0 && NetCDF.nc_inq_varid(ncid, "Longitude", out varid) == 0) return true;

            return false;
        }

        // Get the dates from the new or old DA and TA formats
        public static DateTime[] GetDates(int ncid)
        {
            DateTime[] Dates;

            // Dates are stored as as ticks in later versions 
            //  or as days from start date and milliseconds of the day for old TA
            //  or as seconds from the start date for old DA
            if (VarExists(ncid, "DateTime"))
            {
                // Get the length of the DateTime dimension - the number of points in the file
                NetCDF.nc_inq_dimid(ncid, "DateTime", out int dimid);
                NetCDF.nc_inq_dimlen(ncid, dimid, out int TotPoints);
                long[] ticks = new long[TotPoints];
                Dates = new DateTime[TotPoints];
                Get_long(ncid, "DateTime", ticks);

                for (int i = 0; i < Dates.Length; i++) Dates[i] = new DateTime(ticks[i]);
            }
            else if (VarExists(ncid, "Date") && VarExists(ncid, "Time"))
            {
                NetCDF.nc_inq_dimid(ncid, "Days", out int dimid);
                NetCDF.nc_inq_dimlen(ncid, dimid, out int TotPoints);
                short[] Days = new short[TotPoints];
                int[] Seconds = new int[TotPoints];
                Dates = new DateTime[TotPoints];
                DateTime StartDate = DateTime.Parse(GetVarAttribute(ncid, "Date", "units").Substring(11, 10));
                Get_short(ncid, "Date", Days);
                Get_int(ncid, "Time", Seconds);

                for (int i = 0; i < Seconds.Length; i++) Dates[i] = StartDate.AddDays(Days[i]).AddMilliseconds(Seconds[i]);
            }
            else
            {
                DateTime StartDate = DateTime.Parse(GetVarAttribute(ncid, "Date", "units").Substring(14));
                NetCDF.nc_inq_dimid(ncid, "Date", out int dimid);
                NetCDF.nc_inq_dimlen(ncid, dimid, out int TotPoints);
                int[] Seconds = new int[TotPoints];
                Dates = new DateTime[TotPoints];
                Get_int(ncid, "Date", Seconds);

                for (int i = 0; i < Seconds.Length; i++) Dates[i] = StartDate.AddSeconds(Seconds[i]);
            }

            return Dates;
        }

        // Close is inlcuded just for completeness
        public static void CloseFile(int ncid)
        {
            NetCDF.nc_close(ncid);
        }

        #region NH Extensions
        // These methods wrap up some NetCDF funciotn calls that make them easier to use
        //  but less robust - they will be fine if we know we are using a good MBA NetCDF file
        // Get a global attribute
        public static string GetGlobalAttribute(int ncid, string p_AttName)
        {
            if (NetCDF.nc_inq_att(ncid, NetCDF.NC_GLOBAL, p_AttName, out NetCDF.NcType type, out int len) != 0) return string.Empty;
            StringBuilder sb = new StringBuilder(len);
            if (NetCDF.nc_get_att_text(ncid, NetCDF.NC_GLOBAL, p_AttName, sb) != 0) return string.Empty;
            return sb.ToString().Substring(0, len);
        }

        // Get a variable attribute
        public static string GetVarAttribute(int ncid, string VarName, string p_AttName)
        {
            if (NetCDF.nc_inq_varid(ncid, VarName, out int varid) != 0) return string.Empty;
            if (NetCDF.nc_inq_att(ncid, varid, p_AttName, out NetCDF.NcType type, out int len) != 0) return string.Empty;
            StringBuilder sb = new StringBuilder(len);
            if (NetCDF.nc_get_att_text(ncid, varid, p_AttName, sb) != 0) return string.Empty;
            return sb.ToString().Substring(0, len);
        }

        // Check if a variable exists
        public static bool VarExists(int ncid, string VarName)
        {
            return NetCDF.nc_inq_varid(ncid, VarName, out int varid) == 0;
        }

        // Get int data
        public static void Get_int(int ncid, string VarName, int[] data)
        {
            NetCDF.nc_inq_varid(ncid, VarName, out int varid);
            NetCDF.nc_get_var_int(ncid, varid, data);
        }

        // Get float data
        public static void Get_float(int ncid, string VarName, float[] data)
        {
            NetCDF.nc_inq_varid(ncid, VarName, out int varid);
            NetCDF.nc_get_var_float(ncid, varid, data);
        }

        // Get double data
        public static void Get_double(int ncid, string VarName, double[] data)
        {
            NetCDF.nc_inq_varid(ncid, VarName, out int varid);
            NetCDF.nc_get_var_double(ncid, varid, data);
        }

        // Get short data
        public static void Get_short(int ncid, string VarName, short[] data)
        {
            NetCDF.nc_inq_varid(ncid, VarName, out int varid);
            NetCDF.nc_get_var_short(ncid, varid, data);
        }

        // Get long data
        public static void Get_long(int ncid, string VarName, long[] data)
        {
            NetCDF.nc_inq_varid(ncid, VarName, out int varid);
            NetCDF.nc_get_var_longlong(ncid, varid, data);
        }

        // Get string data
        public static void Get_string(int ncid, string VarName, string[] data)
        {
            byte[] bytes = new byte[data.Length];
            NetCDF.nc_inq_varid(ncid, VarName, out int varid);
            NetCDF.nc_get_var_text(ncid, varid, bytes);
            bytes.CopyTo(data, 0);
        }

        // Get byte data
        public static void Get_byte(int ncid, string VarName, byte[] data)
        {
            NetCDF.nc_inq_varid(ncid, VarName, out int varid);
            NetCDF.nc_get_var_ubyte(ncid, varid, data);
        }


        // Methods to write data
        public static void Put_GlobalAttribute(int ncid, string AttName, string AttValue)
        {
            NetCDF.nc_put_att_text(ncid, NetCDF.NC_GLOBAL, AttName, AttValue.Length, AttValue);
        }

        public static void Put_VarAttribute(int ncid, int varid, string AttName, string AttValue)
        {
            NetCDF.nc_put_att_text(ncid, varid, AttName, AttValue.Length, AttValue);
        }

        #endregion

        #region Helper methods
        // Check the dlls are installed
        public static bool CheckNetCDF()
        {
            // Check if it exists
            if (NetCDF_OK) return true;

            if (File.Exists(@"C:\Windows\SysWOW64\netcdf.dll") || File.Exists(@"C:\Windows\System32\netcdf.dll"))
            {
                NetCDF_OK = true;
                return true;
            }

            MessageBox.Show("The NetCDF dlls need installing."
                            + "\nYou can copy the files yourself from\nDropbox\\Software\\Programs\\NetCDF dll\\"
                            + "to C:\\Windows\\SysWOW64 (for 64 bit Windows) or to c:\\Windows\\System32."
                            + "\nYou need hdf.dll, hdf5.dll, netcdf.dll and zlib.dll."
                            + "\n, or you can ask Nick H :-)",
                            "Installation error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            NetCDF_OK = false;
            return false;
        }

        #endregion
    }
}
