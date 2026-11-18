import { z } from "zod";
export const password = z
  .string()
  .min(12, "Use at least 12 characters.")
  .max(128)
  .regex(/[a-zA-Z]/, "Add a letter.")
  .regex(/[0-9]/, "Add a number.");
export const email = z.email("Enter a valid email address.").max(254);
export const registrationSchema = z.object({
  full_name: z.string().trim().min(2, "Enter your full name.").max(120),
  email,
  password,
  country: z.string().trim().min(2, "Enter your country.").max(80),
  institution: z.string().max(160),
  user_type: z.enum(["student", "developer", "candidate"]),
});
