import { verify } from './middleware';
import { honoVerify } from './hono';
import type { VerifyOptions } from './types';

export const AgentTrust = {
  verify: (options?: VerifyOptions) => verify(options),
  honoVerify: (options?: VerifyOptions) => honoVerify(options),
};

export { verify } from './middleware';
export { honoVerify } from './hono';
export type { VerifyOptions, AgentVerification } from './types';
