using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using System.Globalization;

namespace My3DApp.Controllers
{
    public class ViewerController : Controller
    {
        public IActionResult Show(float side)
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"Scripts/python/generator.py cube --size {side} --as-base64",
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            string base64 = "";

            using (var process = Process.Start(psi))
            {
                if (process != null)
                {
                    base64 = process.StandardOutput.ReadToEnd();
                    process.WaitForExit();
                }
            }


            ViewBag.ModelBase64 = base64?.Trim();

            return View();
        }
    }
}
