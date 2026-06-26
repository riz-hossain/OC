# C# Portable Testcase Reader

`ZkmePortableTestcaseReader.cs` reads `zkme.portable-testcase.v1` files with `System.Text.Json`.

It gives .NET teams a small adapter surface for wiring generated ZKME cases into NUnit, xUnit, MSTest, Playwright for .NET, Selenium, Appium, API, or DB runners.

```bash
dotnet new console -n ZkmeReaderScratch
cp qa/automation/local-runner/adapters/csharp/ZkmePortableTestcaseReader.cs ZkmeReaderScratch/Program.cs
dotnet run --project ZkmeReaderScratch -- qa/automation/local-runner/test-cases/SAMPLE_PORTABLE_TESTCASE.json
```
