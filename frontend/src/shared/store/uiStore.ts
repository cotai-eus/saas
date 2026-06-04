import { create } from 'zustand';
import type { CampaignStatus } from '../api/types';

interface UIState {
  sidebarCollapsed: boolean;
  campaignsFilter: CampaignStatus | 'all';
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setCampaignsFilter: (filter: CampaignStatus | 'all') => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  campaignsFilter: 'all',
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  setCampaignsFilter: (filter) => set({ campaignsFilter: filter }),
}));
