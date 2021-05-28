using ContosoHR.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System;
using System.IO;
using System.Linq;
using System.Linq.Dynamic.Core;
using Microsoft.EntityFrameworkCore;
using System.Data;
using Microsoft.Data.SqlClient;
using System.Globalization;

namespace ContosoHR.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class EmployeeController : ControllerBase
    {
        private readonly ContosoHRContext context;
        public EmployeeController(ContosoHRContext context)
        {
            this.context = context;
        }
        [HttpPost]
        public IActionResult GetEmployees()
        {
            try
            {
                var draw = Request.Form["draw"].FirstOrDefault();
                var start = Request.Form["start"].FirstOrDefault();
                var length = Request.Form["length"].FirstOrDefault();
                var sortColumn = Request.Form["columns[" + Request.Form["order[0][column]"].FirstOrDefault() + "][name]"].FirstOrDefault();
                var sortColumnDirection = Request.Form["order[0][dir]"].FirstOrDefault();
                var searchValue = Request.Form["search[value]"].FirstOrDefault();
                int pageSize = length != null ? Convert.ToInt32(length) : 0;
                int skip = start != null ? Convert.ToInt32(start) : 0;
                int recordsTotal = 0;

                string salaryRange = Request.Form["columns[4][search][value]"]; // NOTE: it must match .column(8) in Index.cshtml


                int from = 0, to = 100000;

                if (!string.IsNullOrEmpty(salaryRange))
                {
                    from = Convert.ToInt32(salaryRange.Split(':')[0]);
                    to = Convert.ToInt32(salaryRange.Split(':')[1]);
                }

                var ssnSearchPattern = new SqlParameter();
                ssnSearchPattern.ParameterName = @"@SSNSearchPattern";
                ssnSearchPattern.DbType = DbType.AnsiStringFixedLength;
                ssnSearchPattern.Direction = ParameterDirection.Input;
                ssnSearchPattern.Value = "%" + searchValue + "%";
                ssnSearchPattern.Size = ssnSearchPattern.Value.ToString().Length;

                var nameSearchPattern = new SqlParameter();
                nameSearchPattern.ParameterName = @"@NameSearchPattern";
                nameSearchPattern.DbType = DbType.String;
                nameSearchPattern.Direction = ParameterDirection.Input;
                nameSearchPattern.Value = "%" + searchValue + "%";
                nameSearchPattern.Size = nameSearchPattern.Value.ToString().Length;

                var minSalary = new SqlParameter();
                minSalary.ParameterName = @"@MinSalary";
                minSalary.DbType = DbType.Currency;
                minSalary.Direction = ParameterDirection.Input;
                minSalary.Value = from;

                var maxSalary = new SqlParameter();
                maxSalary.ParameterName = @"@MaxSalary";
                maxSalary.DbType = DbType.Currency;
                maxSalary.Direction = ParameterDirection.Input;
                maxSalary.Value = to;

                var employeeData = context.Employees.FromSqlRaw(
                    @"SELECT [EmployeeID], [SSN], [FirstName], [LastName], [Salary] FROM [dbo].[Employees] WHERE ([SSN] LIKE @SSNSearchPattern OR [LastName] LIKE @NameSearchPattern) AND [Salary] BETWEEN @MinSalary AND @MaxSalary"
                    , ssnSearchPattern
                    , nameSearchPattern
                    , minSalary
                    , maxSalary);

                // ###############################################################################################

                // Intercepting query string
                var queryString = $"SELECT [EmployeeID], [SSN], [FirstName], [LastName], [Salary] " +
                                  $"FROM [dbo].[Employees] " +
                                  $"WHERE " +
                                  $"([SSN] LIKE {ssnSearchPattern.Value} OR " +
                                  $"[LastName] LIKE {nameSearchPattern.Value}) AND " +
                                  $"[Salary] BETWEEN {minSalary.Value} AND " +
                                  $"{maxSalary.Value}";

                System.Diagnostics.Debug.WriteLine(queryString);
                string localTime = DateTime.Now.ToString();
                string domainUserName = System.Security.Principal.WindowsIdentity.GetCurrent().Name;
                string userName = domainUserName.Substring(domainUserName.IndexOf("\\") + 1);

                // Create log record
                string queryRecord = localTime + " | " + userName + "@contoso.com" + " | " + queryString;

                // Append text to an new/existing file named "querylogs.txt"
                string logPath = "D:\\ContosoHR_logs";

                using (StreamWriter outputFile = new StreamWriter(Path.Combine(logPath, "querylogs.txt"), true))
                {
                    outputFile.WriteLine(queryRecord);
                }

                // ###############################################################################################

                if (!(string.IsNullOrEmpty(sortColumn) && string.IsNullOrEmpty(sortColumnDirection)))
                {
                    employeeData = employeeData.OrderBy(sortColumn + " " + sortColumnDirection);
                }

                recordsTotal = employeeData.Count();
                var data = employeeData.Skip(skip).Take(pageSize).ToList();
                var jsonData = new { draw = draw, recordsFiltered = recordsTotal, recordsTotal = recordsTotal, data = data };
                return Ok(jsonData);
            }
            catch (Exception ex)
            {
                Console.Write(ex.Message);
                return new JsonResult(new { error = ex.ToString() });
            }
        }
    }
}