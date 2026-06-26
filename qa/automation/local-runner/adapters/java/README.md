# Java Portable Testcase Reader

`ZkmePortableTestcaseReader.java` is a dependency-free reader for `zkme.portable-testcase.v1` JSON files.

It validates the core schema fields and prints testcase/step summaries so Java teams can plug ZKME generated cases into JUnit, TestNG, RestAssured, Selenium, Appium, or internal runners.

```bash
javac qa/automation/local-runner/adapters/java/ZkmePortableTestcaseReader.java
java -cp qa/automation/local-runner/adapters/java ZkmePortableTestcaseReader qa/automation/local-runner/test-cases/SAMPLE_PORTABLE_TESTCASE.json
```
