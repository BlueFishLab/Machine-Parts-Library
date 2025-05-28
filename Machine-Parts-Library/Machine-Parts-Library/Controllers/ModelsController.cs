using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using System.Text.Json;

namespace YourApp.Controllers
{
    public class ModelsController : Controller
    {
        public IActionResult ExportInfo()
        {
            var scriptPath = Path.Combine(Directory.GetCurrentDirectory(), "Scripts", "python", "generator.py");

            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\" --export-info", // TYLKO --export-info, bez dodatkowych parametrów
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            try
            {
                using var process = Process.Start(psi);
                var output = process.StandardOutput.ReadToEnd();
                var error = process.StandardError.ReadToEnd();
                process.WaitForExit();

                if (!string.IsNullOrWhiteSpace(error))
                {
                    return Content($"Błąd Pythona:\n{error}");
                }

                // Zakładamy że skrypt wypisuje JSON na stdout
                var json = JsonDocument.Parse(output);
                return Json(json.RootElement);
            }
            catch (Exception ex)
            {
                return Content($"Wyjątek systemowy:\n{ex.Message}");
            }
        }
    }
}
