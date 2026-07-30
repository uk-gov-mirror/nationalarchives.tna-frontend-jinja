import { test, expect } from "@playwright/test";

test("@django consumer app index loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Django example app" })).toBeVisible();
});

test("@django conditional form shows validation", async ({ page }) => {
  await page.goto("/forms/conditional/");
  await page.getByRole("radio", { name: "Email" }).click();
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page.getByText("Enter an email address")).toBeVisible();
});
