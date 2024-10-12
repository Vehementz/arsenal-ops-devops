Here’s a structured and concise guide for **Playwright**, mimicking the style used for Helm, Molecule, Checkov, and Trivy:

# Playwright

Playwright is an end-to-end testing framework for web applications. It enables fast and reliable cross-browser testing by controlling Chromium, Firefox, and WebKit browsers with a single API.

#platform/multiple #target/WebApps #cat/Testing

% playwright, end-to-end testing, automation, web apps

## Playwright - Install Playwright

Install Playwright and its browser binaries.

```
npm install @playwright/test
npx playwright install
```

## Playwright - Create a New Test

Create a new Playwright test file.

```
npx playwright codegen
```

This will open a browser where you can interact with your web application, and Playwright will record your actions and generate the corresponding test code.

## Playwright - Run Tests

Run all tests in your project using the Playwright Test Runner.

```
npx playwright test
```

Run a specific test file:

```
npx playwright test <test-file>.spec.js
```

## Playwright - Run Tests in Headed Mode

Run tests with the browser's UI visible (headed mode).

```
npx playwright test --headed
```

## Playwright - Run Tests in a Specific Browser

Run Playwright tests in a specific browser like Chromium, Firefox, or WebKit.

```
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Playwright - Record a Trace

Generate a trace of the test execution for debugging purposes.

```
npx playwright test --trace on
```

View a previously generated trace:

```
npx playwright show-trace <trace-file>
```

## Playwright - Run Tests in Debug Mode

Run Playwright tests in debug mode with detailed logs and the ability to pause test execution.

```
npx playwright test --debug
```

## Playwright - Generate Test Reports

Generate and view HTML reports for your tests.

```
npx playwright test --reporter=html
```

After running the tests, you can open the report:

```
npx playwright show-report
```

## Playwright - Take Screenshots on Test Failure

Enable automatic screenshots on test failures.

```
npx playwright test --screenshot=on
```

## Playwright - Test on Mobile Devices

Simulate a mobile device environment for your tests by specifying a device type.

```
npx playwright test --device="iPhone 12"
```
