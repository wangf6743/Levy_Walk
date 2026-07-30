using System;
using System.Runtime.InteropServices;
using System.Text;

// Modified to add the put_var1 methods
// Further modifed to include the Constants

namespace Microsoft.Research.ScientificDataSet.NetCDF
{
    public static class NetCDF
    {
        #region Constants
        /// <summary>
        /// 'size' argument to ncdimdef for an unlimited dimension
        /// </summary>
        public const int NC_UNLIMITED = 0;

        /// <summary>
        /// attribute id to put/get a global attribute
        /// </summary>
        public const int NC_GLOBAL = -1;

        /// <summary>
        /// The netcdf external data types
        /// </summary>
        public enum NcType : int
        {
            /// <summary>signed 1 byte intege</summary>
            NC_BYTE = 1,
            /// <summary>ISO/ASCII character</summary>
            NC_CHAR = 2,
            /// <summary>signed 2 byte integer</summary>
            NC_SHORT = 3,
            /// <summary>signed 4 byte integer</summary>
            NC_INT = 4,
            /// <summary>single precision floating point number</summary>
            NC_FLOAT = 5,
            /// <summary>double precision floating point number</summary>
            NC_DOUBLE = 6,
            /// <summary>signed 8-byte int</summary>
            NC_INT64 = 10,
            /// <summary>string</summary>
            NC_STRING = 12
        }

        public static Type GetCLRType(NcType ncType)
        {
            switch (ncType)
            {
                case NcType.NC_BYTE:
                    return typeof(byte);
                case NcType.NC_CHAR:
                    return typeof(sbyte);
                case NcType.NC_SHORT:
                    return typeof(short);
                case NcType.NC_INT:
                    return typeof(int);
                case NcType.NC_INT64:
                    return typeof(long);
                case NcType.NC_FLOAT:
                    return typeof(float);
                case NcType.NC_DOUBLE:
                    return typeof(double);
                case NcType.NC_STRING:
                    return typeof(string);
                default:
                    throw new ApplicationException("Unknown nc type");
            }
        }

        public static NcType GetNcType(Type type)
        {
            switch (Type.GetTypeCode(type))
            {
                case TypeCode.Double:
                    return NcType.NC_DOUBLE;

                case TypeCode.Single:
                    return NcType.NC_FLOAT;

                case TypeCode.Int64:
                    return NcType.NC_INT64;

                case TypeCode.Int32:
                    return NcType.NC_INT;

                case TypeCode.Int16:
                    return NcType.NC_SHORT;

                case TypeCode.Byte:
                    return NcType.NC_BYTE;

                case TypeCode.SByte:
                    return NcType.NC_CHAR;

                case TypeCode.String:
                    return NcType.NC_STRING;

                case TypeCode.DateTime:
                    return NcType.NC_INT64;


                default:
                    throw new NotSupportedException("Not supported type of data.");
            }
        }

        public enum CreateMode : int
        {
            NC_NOWRITE = 0,
            /// <summary>read & write</summary>
            NC_WRITE = 0x0001,
            NC_CLOBBER = 0,
            /// <summary>Don't destroy existing file on create</summary>
            NC_NOCLOBBER = 0x0004,
            NC_DISKLESS = 0x0008,  
            /// <summary>argument to ncsetfill to clear NC_NOFILL</summary>
            NC_FILL = 0,
            /// <summary>Don't fill data section an records</summary>
            NC_NOFILL = 0x0100,
            /// <summary>Use locking if available</summary>
            NC_LOCK = 0x0400,
            /// <summary>Share updates, limit cacheing</summary>
            NC_SHARE = 0x0800,
            NC_64BIT_OFFSET = 0x0200,
            /// <summary>Enforce strict netcdf-3 rules</summary>
            NC_CLASSIC = 0x0100,
            /// <summary>causes netCDF to create a HDF5/NetCDF-4 file</summary>
            NC_NETCDF4 = 0x1000
        }

        public enum ResultCode : int
        {
            /// <summary>No Error</summary>
            NC_NOERR = 0,
            /// <summary>Invalid dimension id or name</summary>
            NC_EBADDIM = -46,
            /// <summary>Attribute not found</summary>
            NC_ENOTATT = -43,
        }

        /// <summary>
        ///	Default fill values, used unless _FillValue attribute is set.
        /// These values are stuffed into newly allocated space as appropriate.
        /// The hope is that one might use these to notice that a particular datum
        /// has not been set.
        /// </summary>
        public static class FillValues
        {
            public const byte NC_FILL_BYTE = 255;
            public const char NC_FILL_CHAR = (char)0;
            public const short NC_FILL_SHORT = -32767;
            public const int NC_FILL_INT = -2147483647;
            public const float NC_FILL_FLOAT = 9.96921E+36f;    /* near 15 * 2^119 */
            public const double NC_FILL_DOUBLE = 9.969209968386869E+36;
        }


        ///<summary>These maximums are enforced by the interface, to facilitate writing
        ///applications and utilities.  However, nothing is statically allocated to
        ///these sizes internally.</summary>
        public enum Limits
        {
            /// <summary>max dimensions per file </summary>
            NC_MAX_DIMS = 10,
            /// <summary>max global or per variable attributes </summary>
            NC_MAX_ATTRS = 2000,
            /// <summary>max variables per file</summary>
            NC_MAX_VARS = 2000,
            /// <summary>max length of a name </summary>
            NC_MAX_NAME = 128,
            /// <summary>max per variable dimensions </summary>
            NC_MAX_VAR_DIMS = 10
        }

        #endregion

        #region Methods
        // This method does not work for x64
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern string nc_inq_libvers();
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_open(string path, CreateMode mode, out int ncidp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_create(string path, CreateMode mode, out int ncidp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_close(int ncidp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_sync(int ncid);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_enddef(int ncid);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_redef(int ncid);

        // This method taken from the Microsoft Scientific data set resources - clearly it is too difficult
        //  to handle a string as a return value from a method, otherwise they would not have gone to all this trouble.
        public static string nc_strerror(int ncerror)
        {
            switch (ncerror)
            {
                case (0): return "No error";
                case (-1): return "Returned for all errors in the v2 API";
                case (-33): return "Not a netcdf id";
                case (-34): return "Too many netcdfs open";
                case (-35): return "netcdf file exists && NC_NOCLOBBER";
                case (-36): return "Invalid Argument";
                case (-37): return "Write to read only";
                case (-38): return "Operation not allowed in data mode";
                case (-39): return "Operation not allowed in define mode";
                case (-40): return "Index exceeds dimension bound. Consider cloning the file into NetCDF 4 format to enable data extdending (e.g. with sds copy command)";
                case (-41): return "NC_MAX_DIMS exceeded";
                case (-42): return "String match to name in use";
                case (-43): return "Attribute not found";
                case (-44): return "NC_MAX_ATTRS exceeded";
                case (-45): return "Not a netcdf data type. Some types are not supported by the classic NetCDF format. Consider cloning the file into NetCDF 4 format to enable use of all supported types (e.g. with sds copy command)";
                case (-46): return "Invalid dimension id or name";
                case (-47): return "NC_UNLIMITED in the wrong index";
                case (-48): return "NC_MAX_VARS exceeded";
                case (-49): return "Variable not found";
                case (-50): return "Action prohibited on NC_GLOBAL varid";
                case (-51): return "Not a netcdf file";
                case (-52): return "In Fortran, string too short";
                case (-53): return "NC_MAX_NAME exceeded";
                case (-54): return "NC_UNLIMITED size already in use";
                case (-55): return "nc_rec op when there are no record vars";
                case (-56): return "Attempt to convert between text & numbers";
                case (-57): return "Start+count exceeds dimension bound";
                case (-58): return "Illegal stride";
                case (-59): return "Attribute or variable name contains illegal characters";
                case (-60): return "Math result not representable";
                case (-61): return "Memory allocation (malloc) failure";
                case (-62): return "One or more variable sizes violate format constraints";
                case (-63): return "Invalid dimension size";
                case (-64): return "File likely truncated or possibly corrupted";
                case (-65): return "Unknown axis type.";
                // DAP errors
                case (-66): return "Generic DAP error";
                case (-67): return "Generic libcurl error";
                case (-68): return "Generic IO error";
                // netcdf-4 errors
                case (-100): return "NetCDF4 error";
                case (-101): return "Error at HDF5 layer.";
                case (-102): return "Can't read.";
                case (-103): return "Can't write.";
                case (-104): return "Can't create.";
                case (-105): return "Problem with file metadata.";
                case (-106): return "Problem with dimension metadata.";
                case (-107): return "Problem with attribute metadata.";
                case (-108): return "Problem with variable metadata.";
                case (-109): return "Not a compound type.";
                case (-110): return "Attribute already exists.";
                case (-111): return "Attempting netcdf-4 operation on netcdf-3 file.";
                case (-112): return "Attempting netcdf-4 operation on strict nc3 netcdf-4 file.";
                case (-113): return "Attempting netcdf-3 operation on netcdf-4 file.";
                case (-114): return "Parallel operation on file opened for non-parallel access.";
                case (-115): return "Error initializing for parallel access.";
                case (-116): return "Bad group ID.";
                case (-117): return "Bad type ID.";
                case (-118): return "Type has already been defined and may not be edited.";
                case (-119): return "Bad field ID.";
                case (-120): return "Bad class.";
                case (-121): return "Mapped access for atomic types only.";
                case (-122): return "Attempt to define fill value when data already exists.";
                case (-123): return "Attempt to define var properties, like deflate, after enddef.";
                case (-124): return "Probem with HDF5 dimscales.";
                case (-125): return "No group found.";
                case (-126): return "Can't specify both contiguous and chunking.";
                case (-127): return "Bad chunksize.";
                case (-128): return "NetCDF4 error";
                default: return "NetCDF error " + ncerror;
            }
        }

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq(int ncid, out int ndims, out int nvars, out int ngatts, out int unlimdimid);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_def_var(int ncid, string name, NcType xtype, int ndims, int[] dimids, out int varidp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_var(int ncid, int varid, StringBuilder name, out NcType type, out int ndims, int[] dimids, out int natts);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_varids(int ncid, out int nvars, int[] varids);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_vartype(int ncid, int varid, out NcType xtypep);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_varnatts(int ncid, int varid, out int nattsp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_varid(int ncid, string name, out int varidp);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_ndims(int ncid, out int ndims);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_nvars(int ncid, out int nvars);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_varname(int ncid, int varid, StringBuilder name);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_varndims(int ncid, int varid, out int ndims);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_vardimid(int ncid, int varid, int[] dimids);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_var_fill(int ncid, int varid, out int no_fill, out object fill_value);


        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_natts(int ncid, out int ngatts);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_unlimdim(int ncid, out int unlimdimid);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_format(int ncid, out int format);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_attname(int ncid, int varid, int attnum, StringBuilder name);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_att(int ncid, int varid, string name, out NcType type, out int length);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_att_text(int ncid, int varid, string name, StringBuilder value);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_att_schar(int ncid, int varid, string name, sbyte[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_att_short(int ncid, int varid, string name, short[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_att_int(int ncid, int varid, string name, int[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_att_float(int ncid, int varid, string name, float[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_att_double(int ncid, int varid, string name, double[] data);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_att_text(int ncid, int varid, string name, int len, string tp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_att_double(int ncid, int varid, string name, NcType type, int len, double[] tp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_att_int(int ncid, int varid, string name, NcType type, int len, int[] tp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_att_short(int ncid, int varid, string name, NcType type, int len, short[] tp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_att_float(int ncid, int varid, string name, NcType type, int len, float[] tp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_att_byte(int ncid, int varid, string name, NcType type, int len, sbyte[] tp);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_def_dim(int ncid, string name, int len, out int dimidp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_dim(int ncid, int dimid, StringBuilder name, out int length);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_dimname(int ncid, int dimid, StringBuilder name);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_dimid(int ncid, string name, out int dimid);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_inq_dimlen(int ncid, int dimid, out int length);


        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_text(int ncid, int varid, byte[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_schar(int ncid, int varid, sbyte[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_short(int ncid, int varid, short[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_int(int ncid, int varid, int[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_long(int ncid, int varid, long[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_float(int ncid, int varid, float[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_double(int ncid, int varid, double[] data);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_text(int ncid, int varid, int[] index, out byte data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_schar(int ncid, int varid, int[] index, out sbyte data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_short(int ncid, int varid, int[] index, out short data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_int(int ncid, int varid, int[] index, out int data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_long(int ncid, int varid, int[] index, out long data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_float(int ncid, int varid, int[] index, out float data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_double(int ncid, int varid, int[] index, out double data);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_double(int ncid, int varid, int[] start, int[] count, double[] dp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_float(int ncid, int varid, int[] start, int[] count, float[] fp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_short(int ncid, int varid, int[] start, int[] count, short[] sp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_int(int ncid, int varid, int[] start, int[] count, int[] ip);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_long(int ncid, int varid, int[] start, int[] count, long[] lp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_ubyte(int ncid, int varid, int[] start, int[] count, byte[] bp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_schar(int ncid, int varid, int[] start, int[] count, sbyte[] cp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_string(int ncid, int varid, int[] start, int[] count, string[] sp);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_double(int ncid, int varid, double[] dp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_float(int ncid, int varid, float[] fp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_short(int ncid, int varid, short[] sp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_int(int ncid, int varid, int[] ip);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_long(int ncid, int varid, long[] lp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_ubyte(int ncid, int varid, byte[] bp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_schar(int ncid, int varid, sbyte[] cp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_string(int ncid, int varid, string[] sp);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_text(int ncid, int varid, int[] start, int[] count, byte[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_schar(int ncid, int varid, int[] start, int[] count, sbyte[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_short(int ncid, int varid, int[] start, int[] count, short[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_ubyte(int ncid, int varid, int[] start, int[] count, byte[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_long(int ncid, int varid, int[] start, int[] count, long[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_int(int ncid, int varid, int[] start, int[] count, int[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_float(int ncid, int varid, int[] start, int[] count, float[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_double(int ncid, int varid, int[] start, int[] count, double[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_string(int ncid, int varid, int[] start, int[] count, string[] data);

        #endregion

        #region NH Methods
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_double(int ncid, int varid, int[] index, double dp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_float(int ncid, int varid, int[] index, float fp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_short(int ncid, int varid, int[] index, short sp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_int(int ncid, int varid, int[] index, int ip);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_long(int ncid, int varid, int[] index, long lp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_ubyte(int ncid, int varid, int[] index, byte bp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_schar(int ncid, int varid, int[] index, sbyte cp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_string(int ncid, int varid, int[] index, string sp);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_longlong(int ncid, int varid, long[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_vara_longlong(int ncid, int varid, int[] start, int[] count, long[] data);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var1_longlong(int ncid, int varid, int[] index, out long data);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var_longlong(int ncid, int varid, long[] ip);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_vara_longlong(int ncid, int varid, int[] start, int[] count, long[] lp);
        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_put_var1_longlong(int ncid, int varid, int[] index, long lp);

        [DllImport("netcdf.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int nc_get_var_ubyte(int ncid, int varid, byte[] data);
        #endregion
    }
}
