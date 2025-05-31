using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace My3DApp.Controllers
{
    public class ViewerController : Controller
    {
        public IActionResult Show()
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "Scripts/python/main.py cube --size 10 --as-base64 --format glb",
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
