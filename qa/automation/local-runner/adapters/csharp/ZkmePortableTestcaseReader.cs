using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

public static class ZkmePortableTestcaseReader
{
    public static int Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.Error.WriteLine("Usage: ZkmePortableTestcaseReader <portable-testcase.json> [...]");
            return 2;
        }

        var failures = 0;
        foreach (var path in args)
        {
            try
            {
                var testcase = Read(path);
                Console.WriteLine($"{testcase.Id} | {testcase.Title} | steps={testcase.Steps.Count}");
                foreach (var step in testcase.Steps)
                {
                    Console.WriteLine($"  - {step.Id} [{step.Adapter}] {step.Intent}");
                }
            }
            catch (Exception ex)
            {
                failures += 1;
                Console.Error.WriteLine($"{path}: {ex.Message}");
            }
        }

        return failures == 0 ? 0 : 1;
    }

    public static PortableCase Read(string path)
    {
        using var document = JsonDocument.Parse(File.ReadAllText(path));
        var root = document.RootElement;
        if (root.ValueKind != JsonValueKind.Object)
        {
            throw new InvalidOperationException("root JSON value must be an object");
        }

        var schema = GetString(root, "schemaVersion");
        if (schema != "zkme.portable-testcase.v1")
        {
            throw new InvalidOperationException("schemaVersion must be zkme.portable-testcase.v1");
        }

        var id = RequireString(root, "id");
        var title = RequireString(root, "title");
        if (!root.TryGetProperty("steps", out var rawSteps) || rawSteps.ValueKind != JsonValueKind.Array)
        {
            throw new InvalidOperationException("steps must be an array");
        }

        var steps = new List<PortableStep>();
        var index = 1;
        foreach (var step in rawSteps.EnumerateArray())
        {
            if (step.ValueKind != JsonValueKind.Object)
            {
                throw new InvalidOperationException($"step {index} must be an object");
            }
            steps.Add(new PortableStep(
                GetString(step, "id", $"step-{index}"),
                GetString(step, "adapter", "manual"),
                GetString(step, "intent", GetString(step, "action", $"Step {index}")),
                GetString(step, "expected", "")
            ));
            index += 1;
        }

        return new PortableCase(id, title, steps);
    }

    private static string RequireString(JsonElement element, string property)
    {
        var value = GetString(element, property, "");
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new InvalidOperationException($"missing required field: {property}");
        }
        return value;
    }

    private static string GetString(JsonElement element, string property, string fallback = "")
    {
        if (!element.TryGetProperty(property, out var value))
        {
            return fallback;
        }
        return value.ValueKind == JsonValueKind.String ? value.GetString() ?? fallback : value.ToString();
    }

    public sealed record PortableCase(string Id, string Title, IReadOnlyList<PortableStep> Steps);
    public sealed record PortableStep(string Id, string Adapter, string Intent, string Expected);
}
