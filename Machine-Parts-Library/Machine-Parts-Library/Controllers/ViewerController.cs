using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace My3DApp.Controllers
{
    public class ViewerController : Controller
    {
        public IActionResult Show()
        {
            return View();
        }

        [HttpGet]
        public IActionResult GenerateModel(string shape = "cube", int size = 10)
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"Scripts/python/main.py {shape} --size {size} --as-base64 --format glb",
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

            return Content(base64?.Trim());
        }
    }
}
