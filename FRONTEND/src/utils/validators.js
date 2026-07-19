import { z } from 'zod';

// ---- Auth ----

export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export const registerSchema = z.object({
  firstname: z.string().min(1, 'First name is required').max(50),
  middlename: z.string().max(50).optional().or(z.literal('')),
  lastname: z.string().min(1, 'Last name is required').max(50),
  username: z.string().min(3, 'Username must be at least 3 characters').max(30),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((d) => d.password === d.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

export const forgotPasswordSchema = z.object({
  email: z.string().email('Enter a valid email'),
});

export const resetPasswordSchema = z.object({
  token: z.string().min(1, 'Token is required'),
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((d) => d.new_password === d.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

// ---- Users ----

export const userUpdateSchema = z.object({
  firstname: z.string().max(50).optional().or(z.literal('')),
  middlename: z.string().max(50).optional().or(z.literal('')),
  lastname: z.string().max(50).optional().or(z.literal('')),
  username: z.string().max(30).optional().or(z.literal('')),
  email: z.string().email('Enter a valid email').optional().or(z.literal('')),
  password: z.string().min(8).optional().or(z.literal('')),
});

export const deactivateUserSchema = z.object({
  reason: z.string().optional(),
});

// ---- Groups ----

export const groupSchema = z.object({
  name: z.string().min(1, 'Name is required').max(50),
  description: z.string().max(500).optional().or(z.literal('')),
});

// ---- Roles ----

export const roleSchema = z.object({
  name: z.string().min(1, 'Name is required').max(50),
  description: z.string().max(500).optional().or(z.literal('')),
});

// ---- Permissions ----

export const permissionSchema = z.object({
  name: z.string().min(1, 'Name is required').max(50),
  description: z.string().max(500).optional().or(z.literal('')),
});

// ---- Assignment schemas ----

export const assignWithDatesSchema = z.object({
  id: z.number({ required_error: 'Please select an item' }),
  valid_from: z.string().optional(),
  valid_until: z.string().optional(),
});
