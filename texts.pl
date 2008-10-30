use strict;
use utf8;

our $Lang //= 'en';

my $texts = {
  q[.] => {
    ja => '。',
  },
  q[A user who is invited by an administrator of the group can join the group.] => {
    ja => q[グループの管理者が招待した人だけがグループに参加できます。],
  },
  q[A user who is invited or approved by an administrator of the group can join the group.] => {
    ja => q[グループの管理者が招待した人と承認した人だけがグループに参加できます。],
  },
  'Administrative group' => {
    ja => q[管理者グループ],
  },
  q[Any user can join the group.] => {
    ja => q[誰でもこのグループに参加できます。],
  },
  'Approve' => {
    ja => '承認',
  },
  'Cancel invitation' => {
    ja => '招待取消',
  },
  'Cancel the request' => {
    ja => '申請取消',
  },
  'Caution!' => {
    ja => '警告!',
  },
  Change => {
    ja => '変更',
  },
  Create => {
    ja => '作成',
  },
  'Create a new group' => {
    ja => '新しいグループの作成',
  },
  'Create a new user account' => {
    ja => '新しい利用者アカウントの作成',
  },
  Description => {
    ja => '説明',
  },
  'Disable account' => {
    ja => q[アカウントの無効化],
  },
  q[Do you really want to join this group?] => {
    ja => q[本当にこのグループに参加しますか?],
  },
  q[Don't expose any confidential data.] => {
    en => q[Though these properties are only accessible to administrators, you are advised not to expose any confidential data.],
    ja => q[これらの特性は管理者のみが見ることができますが、秘密の情報は記述しないことをお勧めします。],
  },
  'Enable this account' => {
    ja => 'このアカウントを有効にする',
  },
  Error => {
    ja => '誤り',
  },
  Forbidden => {
    en => 'Your access is forbidden',
    ja => 'アクセスは認められていません',
  },
  q[Forbidden (You've logged in as %s)] => {
    en => q[Your access is forbidden (you've logged in as %s)],
    ja => 'アクセスは認められていません (%s としてログインしています)',
  },
  'Formal members' => {
    ja => '正式な参加者',
  },
  'Full name' => {
    ja => '名前',
  },
  Group => {
    ja => 'グループ',
  },
  Groups => {
    ja => 'グループ',
  },
  'Group %s' => {
    ja => 'グループ %s',
  },
  'Group %s registered' => {
    ja => 'グループ %s を登録しました。',
  },
  'Group id' => {
    en => 'Group ID',
    ja => 'グループ識別子',
  },
  'Group id %s is already used' => {
    en => 'Group ID %s is already used',
    ja => 'グループ識別子 %s は既に使われています',
  },
  'Group id %s is invalid; use characters [0-9a-z-]{4,20}' => {
    en => 'Group ID %s is invalid; use 4..20 letters "a".."z", "0".."9", and "-"',
    ja => 'グループ識別子 %s は正しくありません。「a」〜「z」、「0」〜「9」、「-」で構成される 4〜20 文字の文字列でなければなりません',
  },
  'Groups you can join now (without approval)' => {
    ja => 'すぐに参加できる (許可不要の) グループ',
  },
  'Groups you can request to join (approval required to join)' => {
    ja => '参加申請できる (参加許可が必要な) グループ',
  },
  'Groups you have been invited but not joined yet, or you have left' => {
    ja => '招待されているグループ、脱退したグループ',
  },
  'Groups you have joined' => {
    ja => '参加中のグループ',
  },
  'Groups you have requested to join but not approved yet' => {
    ja => '参加申請中 (未許可) のグループ',
  },
  Kick => {
    ja => '追放',
  },
  Invite => {
    ja => '招待',
  },
  'Invite a user' => {
    ja => '招待',
  },
  'Join this group' => {
    ja => 'このグループに入る',
  },
  'Joinning the group %s' => {
    ja => 'グループ %s への参加',
  },
  'Leave this group' => {
    ja => 'このグループから抜ける',
  },
  'Mail address' => {
    ja => 'メイル・アドレス',
  },
  'Member approval policy' => {
    ja => '参加の承認',
  },
  Members => {
    ja => '参加者',
  },
  'New password' => {
    ja => '新しい合言葉',
  },
  No => {
    ja => 'いいえ',
  },
  'Not found' => {
    ja => '見つかりません',
  },
  q[Once you disable your own account, you cannot enable your account by yourself.] => {
    ja => q[自分のアカウントを無効にすると、自分で再度有効にすることはできません。],
  },
  Password => {
    ja => '合言葉',
  },
  'Password must be longer than 3 characters' => {
    ja => '合言葉は4文字以上でなければなりません。',
  },
  Properties => {
    ja => '特性',
  },
  Save => {
    ja => '保存',
  },
  'See %s.' => {
    ja => '%sをご覧ください。',
  },
  'the group information page' => {
    ja => 'グループ情報の頁',
  },
  'The new group is created successfully.' => {
    ja => '新しいグループを作成しました。',
  },
  'Two passwords you input are different' => {
    ja => '2つの合言葉が異なります',
  },
  'Type 4 characters at minimum' => {
    ja => '最低4文字入力してください。',
  },
  'type again' => {
    ja => 'もう一度',
  },
  q[Use [0-9a-z-]{4,20}.] => {
    en => q[Use a string of characters 'a'..'z', '0'..'9', and '-', whose length is in the range 4..10 (inclusive)],
    ja => q[文字「a」〜「z」、「0」〜「9」、「-」を使って 4〜10 文字の文字列を指定してください。],
  },
  'User %s' => {
    ja => '%s さん',
  },
  'User %s registered' => {
    ja => '利用者 %s を登録しました',
  },
  'User id' => {
    ja => '利用者識別子',
  },
  'User id %s is already used' => {
    ja => '利用者識別子 %s は既に使われています',
  },
  'User id %s is invalid; use characters [0-9a-z-]{4,20}' => {
    en => 'User ID %s is invalid; use 4..20 letters "a".."z", "0".."9", and "-"',
    ja => '利用者識別子 %s は正しくありません。「a」〜「z」、「0」〜「9」、「-」で構成される 4〜20 文字の文字列でなければなりません',
  },
  'Users who are invited but not joined or are leaved' => {
    ja => '招待済みで未参加の人達、脱退した人達',
  },
  'Users who are waiting for the approval to join' => {
    ja => '参加申請中 (許可待ち) の人達',
  },
  'Web site URL' => {
    ja => 'Web サイト URL',
  },
  Yes => {
    ja => 'はい',
  },
  'You can change the password.' => {
    ja => '合言葉を変更できます。',
  },
  'your user account information page' => {
    ja => '利用者アカウント情報の頁',
  },
  'Your user account is created successfully.' => {
    ja => '利用者アカウントを作成しました。',
  },
};

sub print_text ($;$) {
  my ($s, $t) = split /%s/, $texts->{$_[0]}->{$Lang} // $_[0], 2;
  print '', htescape ($s);
  if (defined $t) {
    $_[1]->();
    print '', htescape ($t);
  }
} # print_text

1;
