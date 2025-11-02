import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export const Console = {
	log: (...args: unknown[]) => {
		if (process.env.NODE_ENV === 'development') {
			// eslint-disable-next-line no-console
			console.log(...args);
		}
	},
	info: (...args: unknown[]) => {
		if (process.env.NODE_ENV === 'development') {
			// eslint-disable-next-line no-console
			console.info(...args);
		}
	},
	warn: (...args: unknown[]) => {
		if (process.env.NODE_ENV === 'development') {
			// eslint-disable-next-line no-console
			console.warn(...args);
		}
	},
	error: (...args: unknown[]) => {
		if (process.env.NODE_ENV === 'development') {
			// eslint-disable-next-line no-console
			console.error(...args);
		}
	},
};
