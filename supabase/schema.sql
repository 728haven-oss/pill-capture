-- 알약캡쳐 로그인/무료체험 스키마 (Supabase SQL Editor 에 붙여넣고 실행)
-- 가입일(trial_started_at)을 서버에 기록해 앱을 지웠다 깔아도 무료체험이 초기화되지 않게 한다.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  trial_started_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- 본인 행만 읽기/생성 가능. trial_started_at 을 앞당기는 수정은 허용하지 않는다.
drop policy if exists "read own profile" on public.profiles;
create policy "read own profile" on public.profiles
  for select using (auth.uid() = id);

drop policy if exists "insert own profile" on public.profiles;
create policy "insert own profile" on public.profiles
  for insert with check (auth.uid() = id);

-- 가입 시 자동으로 프로필 생성 (앱이 직접 만들지 않아도 됨)
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id) values (new.id) on conflict (id) do nothing;
  return new;
end; $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
