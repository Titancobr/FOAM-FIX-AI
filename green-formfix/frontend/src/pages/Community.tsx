import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Award, Check, ChevronRight, Flame, Medal, Search, Sparkles, Users, Zap } from "lucide-react";
import Navbar from "@/components/Navbar";
import BottomNav from "@/components/BottomNav";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
type Athlete = { user_id: number; username: string; level: number; xp: number; current_streak?: number; best_streak?: number; following?: boolean; friend_status?: string; rank?: number };
type Activity = { username: string; kind: string; detail: string; created_at: string };
type Badge = { key: string; name: string; description: string };
type Dashboard = { user: Athlete & { checked_in: boolean }; tasks: { id: string; title: string; xp: number; done: boolean }[]; badges: Badge[]; activities: Activity[] };
type SocialLists = { incoming: { request_id: number; user: Athlete }[]; outgoing: Athlete[]; friends: Athlete[]; followers: Athlete[]; following: Athlete[] };

const Community = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [uid, setUid] = useState<number>();
  const [dashboard, setDashboard] = useState<Dashboard>();
  const [leaderboard, setLeaderboard] = useState<Athlete[]>([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Athlete[]>([]);
  const [social, setSocial] = useState<SocialLists>({ incoming: [], outgoing: [], friends: [], followers: [], following: [] });
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async (id: number) => {
    const [dashboardResponse, leaderboardResponse, socialResponse] = await Promise.all([
      fetch(`${API}/community/dashboard/${id}`),
      fetch(`${API}/community/leaderboard`),
      fetch(`${API}/community/friends/${id}`),
    ]);
    if (dashboardResponse.ok) setDashboard(await dashboardResponse.json());
    if (leaderboardResponse.ok) setLeaderboard(await leaderboardResponse.json());
    if (socialResponse.ok) setSocial(await socialResponse.json());
  }, []);

  useEffect(() => {
    const raw = localStorage.getItem("fitUser");
    if (!raw) { navigate("/login"); return; }
    try {
      const id = JSON.parse(raw).user_id as number;
      if (!id) { navigate("/login"); return; }
      setUid(id);
      refresh(id).catch(() => {});
    } catch { navigate("/login"); }
  }, [navigate, refresh]);

  const doAction = async (url: string, body?: object) => {
    if (!uid) return false;
    setBusy(true);
    try {
      const response = await fetch(`${API}${url}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not complete action");
      if (data.xp_earned) toast({ title: `+${data.xp_earned} XP earned`, description: "Your fitness progress is on the board." });
      await refresh(uid);
      return true;
    } catch (error) {
      toast({ title: error instanceof Error ? error.message : "Something went wrong", variant: "destructive" });
      return false;
    } finally { setBusy(false); }
  };

  useEffect(() => {
    if (!uid || query.trim().length < 2) { setResults([]); return; }
    const timer = setTimeout(() => fetch(`${API}/community/search?q=${encodeURIComponent(query)}&viewer_id=${uid}`).then((response) => response.json()).then(setResults).catch(() => setResults([])), 250);
    return () => clearTimeout(timer);
  }, [query, uid]);

  const changeRelation = async (person: Athlete, kind: "follow" | "friend") => {
    if (!uid) return;
    const succeeded = await doAction(`/community/${kind === "follow" ? "follow" : "friend-request"}`, { actor_id: uid, target_id: person.user_id });
    if (succeeded) setResults((current) => current.map((row) => row.user_id === person.user_id ? { ...row, following: kind === "follow" ? !person.following : row.following, friend_status: kind === "friend" ? "pending" : row.friend_status } : row));
  };

  const acceptRequest = async (person: Athlete) => {
    if (uid) await doAction("/community/friend-request", { actor_id: uid, target_id: person.user_id });
  };

  const PersonRow = ({ person, rank }: { person: Athlete; rank?: number }) => (
    <div className="flex items-center gap-3 rounded-xl border border-white/5 bg-white/[0.025] px-3 py-3">
      {rank !== undefined && <span className={`w-7 text-center font-mono text-sm ${rank < 4 ? "text-primary" : "text-muted-foreground"}`}>{String(rank).padStart(2, "0")}</span>}
      <div className="flex h-10 w-10 items-center justify-center rounded-full border border-primary/20 bg-primary/10 font-heading text-xl text-primary">{person.username.slice(0, 1).toUpperCase()}</div>
      <Link to={`/community/profile/${person.user_id}`} className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{person.username}</p><p className="text-xs text-muted-foreground">Level {person.level} · {person.xp} XP</p></Link>
      <ChevronRight className="h-4 w-4 text-muted-foreground" />
    </div>
  );

  const Empty = ({ children }: { children: string }) => <p className="rounded-xl border border-dashed border-white/10 px-4 py-7 text-center text-sm text-muted-foreground">{children}</p>;
  const xp = dashboard?.user.xp ?? 0;
  const progress = xp % 100;
  if (!uid) return null;

  return (
    <div className="min-h-screen bg-background pb-28">
      <Navbar />
      <main className="mx-auto max-w-6xl px-5 pb-12 pt-28 md:px-8">
        <motion.header initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div><p className="mb-2 flex items-center gap-2 text-[10px] uppercase tracking-[.28em] text-primary"><Sparkles className="h-3.5 w-3.5" /> FormFix Arena</p><h1 className="text-5xl uppercase sm:text-6xl">Your fitness <span className="text-gradient">circle.</span></h1><p className="mt-2 text-sm text-muted-foreground">Progress together, one workout at a time.</p></div>
          <Link to="/profile" className="rounded-full border border-white/10 px-4 py-2 text-sm text-muted-foreground hover:text-primary">My profile <ChevronRight className="ml-1 inline h-4 w-4" /></Link>
        </motion.header>

        <section className="glass-card mb-5 flex flex-wrap items-center gap-5 px-5 py-4 sm:px-6">
          <div className="flex min-w-[150px] items-center gap-3"><div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 font-heading text-3xl text-primary">{dashboard?.user.level ?? 1}</div><div><p className="text-[10px] uppercase tracking-[.2em] text-muted-foreground">Athlete level</p><p className="font-mono text-sm">{xp} XP</p></div></div>
          <div className="hidden h-9 w-px bg-white/10 sm:block" />
          <div className="min-w-[170px] flex-1"><div className="mb-1 flex justify-between text-[10px] uppercase tracking-wider text-muted-foreground"><span>Next level</span><span>{progress}/100 XP</span></div><div className="h-1.5 overflow-hidden rounded-full bg-white/10"><motion.div initial={{ width: 0 }} animate={{ width: `${progress}%` }} className="h-full rounded-full bg-gradient-to-r from-primary to-cyan-300" /></div></div>
          <div className="flex items-center gap-2 rounded-xl bg-orange-400/10 px-3 py-2 text-orange-300"><Flame className="h-4 w-4" /><span className="font-mono text-sm">{dashboard?.user.current_streak ?? 0} day streak</span></div>
          <div className="flex items-center gap-2 rounded-xl bg-primary/10 px-3 py-2 text-primary"><Users className="h-4 w-4" /><span className="font-mono text-sm">{social.friends.length} friends</span></div>
        </section>

        <Tabs defaultValue="activity" className="space-y-4">
          <TabsList className="grid h-auto w-full grid-cols-4 rounded-2xl border border-white/10 bg-card/80 p-1 sm:w-fit sm:min-w-[620px]">
            <TabsTrigger value="activity" className="rounded-xl py-3 text-xs data-[state=active]:text-primary sm:text-sm">Activity</TabsTrigger>
            <TabsTrigger value="challenges" className="rounded-xl py-3 text-xs data-[state=active]:text-primary sm:text-sm">Daily Challenges</TabsTrigger>
            <TabsTrigger value="badges" className="rounded-xl py-3 text-xs data-[state=active]:text-primary sm:text-sm">Badges & Streaks</TabsTrigger>
            <TabsTrigger value="friends" className="rounded-xl py-3 text-xs data-[state=active]:text-primary sm:text-sm">Friends</TabsTrigger>
          </TabsList>

          <TabsContent value="activity" className="grid gap-4 lg:grid-cols-[1fr_320px]">
            <section className="glass-card p-5 sm:p-6"><div className="mb-4"><p className="text-[10px] uppercase tracking-[.24em] text-primary">Your circle</p><h2 className="text-3xl uppercase">Activity feed</h2><p className="mt-1 text-xs text-muted-foreground">You, your friends, and athletes you follow.</p></div>
              <div className="space-y-1">{dashboard?.activities.length ? dashboard.activities.map((activity, index) => <div key={`${activity.username}-${index}`} className="flex items-start gap-3 border-b border-white/5 py-3 last:border-0"><span className="mt-1.5 h-2 w-2 rounded-full bg-primary shadow-[0_0_12px_hsl(199_89%_48%/.65)]" /><div className="min-w-0"><p className="text-sm"><strong>{activity.username}</strong> <span className="text-muted-foreground">{activity.kind === "workout" ? "finished a workout" : activity.kind === "badge" ? "earned a badge" : "checked in"}</span></p><p className="text-xs text-muted-foreground">{activity.detail}</p></div></div>) : <Empty>Activity from you and your circle will appear here.</Empty>}</div>
            </section>
            <aside className="glass-card p-5"><div className="mb-3 flex items-center justify-between"><div><p className="text-[10px] uppercase tracking-[.2em] text-primary">Global</p><h2 className="text-2xl uppercase">Leaderboard</h2></div><Medal className="h-5 w-5 text-amber-300" /></div><div className="space-y-2">{leaderboard.slice(0, 5).map((person, index) => <PersonRow key={person.user_id} person={person} rank={index + 1} />)}{!leaderboard.length && <Empty>Earn XP to appear here.</Empty>}</div></aside>
          </TabsContent>

          <TabsContent value="challenges"><section className="glass-card p-5 sm:p-6"><div className="mb-5 flex items-center justify-between"><div><p className="text-[10px] uppercase tracking-[.24em] text-primary">Today · Fitness only</p><h2 className="text-3xl uppercase">Daily challenges</h2></div><Zap className="h-5 w-5 text-primary" /></div><div className="grid gap-3 md:grid-cols-2">{dashboard?.tasks.map((task) => <div key={task.id} className="flex items-center gap-4 rounded-2xl border border-white/5 bg-white/[.025] p-4"><div className={`flex h-11 w-11 items-center justify-center rounded-xl ${task.done ? "bg-emerald-400/10 text-emerald-400" : "bg-primary/10 text-primary"}`}>{task.done ? <Check className="h-5 w-5" /> : <Zap className="h-5 w-5" />}</div><div className="min-w-0 flex-1"><p className="font-semibold">{task.title}</p><p className="text-xs text-muted-foreground">+{task.xp} XP · {task.done ? "Completed today" : "In progress"}</p></div>{task.id === "checkin" && !task.done ? <Button size="sm" disabled={busy} onClick={() => doAction(`/community/check-in/${uid}`)}>Check in</Button> : task.id === "workout" && !task.done ? <Button size="sm" variant="outline" disabled={busy} onClick={() => doAction(`/community/task/${uid}/workout`)}>Claim</Button> : <span className="text-xs text-emerald-400">Done</span>}</div>)}</div><Link to="/workouts" className="mt-5 inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-primary">Open workout plans <ChevronRight className="h-4 w-4" /></Link></section></TabsContent>

          <TabsContent value="badges"><section className="glass-card p-5 sm:p-6"><div className="mb-5 flex flex-wrap items-center justify-between gap-3"><div><p className="text-[10px] uppercase tracking-[.24em] text-primary">Consistency and milestones</p><h2 className="text-3xl uppercase">Badges & streaks</h2></div><div className="flex gap-2"><div className="rounded-xl bg-orange-400/10 px-4 py-2 text-center text-orange-300"><Flame className="mx-auto mb-1 h-4 w-4" /><p className="font-mono text-sm">{dashboard?.user.current_streak ?? 0} current</p></div><div className="rounded-xl bg-white/5 px-4 py-2 text-center"><Flame className="mx-auto mb-1 h-4 w-4 text-muted-foreground" /><p className="font-mono text-sm">{dashboard?.user.best_streak ?? 0} best</p></div></div></div><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{dashboard?.badges.map((badge) => <motion.div key={badge.key} initial={{ scale: .96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex items-center gap-3 rounded-xl border border-primary/15 bg-primary/[.04] p-4"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10"><Award className="h-5 w-5 text-primary" /></div><div><p className="text-sm font-semibold">{badge.name}</p><p className="text-xs text-muted-foreground">{badge.description}</p></div></motion.div>)}</div>{!dashboard?.badges.length && <Empty>Complete workouts to unlock your first badge.</Empty>}</section></TabsContent>

          <TabsContent value="friends" className="grid gap-4 lg:grid-cols-[1.1fr_.9fr]"><section className="glass-card p-5 sm:p-6"><div className="mb-4"><p className="text-[10px] uppercase tracking-[.24em] text-primary">Connect</p><h2 className="text-3xl uppercase">Find athletes</h2></div><div className="relative mb-4"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search usernames" className="border-white/10 bg-white/[.03] pl-10" /></div>{results.length > 0 && <div className="space-y-2">{results.map((person) => <div key={person.user_id} className="flex flex-wrap items-center gap-2 rounded-xl border border-white/5 p-3"><div className="min-w-0 flex-1"><Link to={`/community/profile/${person.user_id}`} className="text-sm font-semibold hover:text-primary">{person.username}</Link><p className="text-xs text-muted-foreground">Level {person.level} · {person.xp} XP</p></div><Button size="sm" variant="outline" disabled={busy} onClick={() => changeRelation(person, "follow")}>{person.following ? "Following" : "Follow"}</Button><Button size="sm" disabled={busy || person.friend_status !== "none"} onClick={() => changeRelation(person, "friend")}>{person.friend_status === "pending" ? "Pending" : person.friend_status === "friends" ? "Friends" : "Add friend"}</Button></div>)}</div>}{query.trim().length >= 2 && results.length === 0 && <Empty>No athletes found.</Empty>}{query.trim().length < 2 && <p className="py-2 text-xs text-muted-foreground">Enter at least two characters to search.</p>}</section>
            <section className="glass-card space-y-5 p-5 sm:p-6"><div><p className="text-[10px] uppercase tracking-[.2em] text-primary">Requests</p><h3 className="text-2xl uppercase">Friend requests</h3><div className="mt-3 space-y-2">{social.incoming.map((request) => <div key={request.request_id} className="flex items-center gap-2 rounded-xl bg-white/[.03] p-3"><span className="flex-1 text-sm">{request.user.username}</span><Button size="sm" onClick={() => acceptRequest(request.user)}>Accept</Button></div>)}{social.outgoing.map((person) => <div key={person.user_id} className="rounded-xl bg-white/[.03] p-3 text-sm text-muted-foreground">Request sent to {person.username}</div>)}{social.incoming.length === 0 && social.outgoing.length === 0 && <p className="text-xs text-muted-foreground">No pending requests.</p>}</div></div>
              {[{ title: "Friends", people: social.friends }, { title: "Followers", people: social.followers }, { title: "Following", people: social.following }].map((group) => <div key={group.title}><div className="mb-2 flex items-center justify-between"><h3 className="text-lg uppercase">{group.title}</h3><span className="font-mono text-xs text-muted-foreground">{group.people.length}</span></div><div className="grid gap-2 sm:grid-cols-2">{group.people.slice(0, 6).map((person) => <Link key={person.user_id} to={`/community/profile/${person.user_id}`} className="truncate rounded-lg border border-white/5 bg-white/[.025] p-2.5 text-sm hover:text-primary">{person.username}</Link>)}</div>{group.people.length === 0 && <p className="text-xs text-muted-foreground">No {group.title.toLowerCase()} yet.</p>}</div>)}
            </section>
          </TabsContent>
        </Tabs>
      </main>
      <BottomNav />
    </div>
  );
};
export default Community;
