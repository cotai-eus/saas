export const ENDPOINTS = {
  me: '/me',
  health: '/health',
  channels: '/channels',
  channel: (id: string) => `/channels/${id}`,
  channelQR: (id: string) => `/channels/${id}/qr`,
  channelValidate: (id: string) => `/channels/${id}/validate`,
  messages: '/messages',
  sendMessage: '/messages/send',
  contacts: '/contacts',
  contact: (id: string) => `/contacts/${id}`,
} as const;
