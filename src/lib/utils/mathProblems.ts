export interface MathProblem {
  id: string;
  level: number;
  question: string;
  answer: number;
  solution: string;
}

export interface PlayerState {
  currentFloor: number;
  highestFloor: number;
  diedToday: boolean;
  lastPlayDate: string;
  streak: number;
  totalCorrect: number;
  totalAttempts: number;
}

const BUILTIN: MathProblem[] = [
  { id: 'p1', level: 1, question: '1 + 2 = ?', answer: 3, solution: '1 + 2 = 3 ง่ายนิดเดียว!' },
  { id: 'p2', level: 2, question: '2 + 4 = ?', answer: 6, solution: '2 + 4 = 6 ยังง่ายอยู่!' },
  { id: 'p3', level: 3, question: '4 + 8 = ?', answer: 12, solution: '4 + 8 = 12 เริ่มสนุก!' },
  { id: 'p4', level: 4, question: '12 + 16 = ?', answer: 28, solution: '12 + 16 = 28 เก่งมาก!' },
  { id: 'p5', level: 5, question: '32 + 64 = ?', answer: 96, solution: '32 + 64 = 96 ไปต่อ!' },
  { id: 'p6', level: 6, question: '64 + 256 = ?', answer: 320, solution: '64 + 256 = 320 สุดยอด!' },
];

const STATE_KEY = 'math_tower_state';
const USER_PROBLEMS_KEY = 'math_tower_user_problems';

export function getTodayStr(): string {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function getDefaultState(): PlayerState {
  return {
    currentFloor: 1,
    highestFloor: 1,
    diedToday: false,
    lastPlayDate: '',
    streak: 0,
    totalCorrect: 0,
    totalAttempts: 0,
  };
}

export function loadPlayerState(): PlayerState {
  try {
    const saved = localStorage.getItem(STATE_KEY);
    if (saved) {
      const state = JSON.parse(saved) as PlayerState;
      const today = getTodayStr();
      if (state.lastPlayDate !== today) {
        state.diedToday = false;
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        const yesterdayStr = yesterday.toISOString().split('T')[0];
        if (state.lastPlayDate && state.lastPlayDate !== yesterdayStr) {
          state.streak = 0;
        }
        state.lastPlayDate = today;
        savePlayerState(state);
      }
      return state;
    }
  } catch (e) {
    console.error('loadPlayerState failed:', e);
  }
  const defaultState = getDefaultState();
  defaultState.lastPlayDate = getTodayStr();
  return defaultState;
}

export function savePlayerState(state: PlayerState): void {
  try {
    localStorage.setItem(STATE_KEY, JSON.stringify(state));
  } catch (e) {
    console.error('savePlayerState failed:', e);
  }
}

export function getProblemForLevel(level: number): MathProblem | null {
  const builtin = BUILTIN.find((p) => p.level === level);
  if (builtin) return { ...builtin };
  try {
    const raw = localStorage.getItem(USER_PROBLEMS_KEY);
    if (raw) {
      const userProblems: MathProblem[] = JSON.parse(raw);
      const match = userProblems.find((p) => p.level === level);
      if (match) return { ...match };
    }
  } catch (e) {
    console.error('getProblemForLevel failed:', e);
  }
  return null;
}

export function addUserProblem(problem: MathProblem): void {
  try {
    const raw = localStorage.getItem(USER_PROBLEMS_KEY);
    const problems: MathProblem[] = raw ? JSON.parse(raw) : [];
    problems.push(problem);
    localStorage.setItem(USER_PROBLEMS_KEY, JSON.stringify(problems));
  } catch (e) {
    console.error('addUserProblem failed:', e);
  }
}

export function getMaxBuiltinLevel(): number {
  return Math.max(...BUILTIN.map((p) => p.level));
}

export function getAllBuiltinCount(): number {
  return BUILTIN.length;
}

export function getTimeUntilReset(): string {
  const now = new Date();
  const midnight = new Date(now);
  midnight.setDate(midnight.getDate() + 1);
  midnight.setHours(0, 0, 0, 0);
  const diff = midnight.getTime() - now.getTime();
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}
