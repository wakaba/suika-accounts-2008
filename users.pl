use strict;

my $mail_from = q<webmaster@suika.fam.cx>;
my $mail_to = q<webmaster@suika.fam.cx>;
my $subject_prefix = q<[suika.fam.cx account]>;

my $user_data_dir_name = 'data/';
my $user_prop_file_suffix = '.user';

my $group_data_dir_name = 'data/';
my $group_prop_file_suffix = '.group';

my $htpasswd_file_name = 'data/htpasswd';
my $htgroup_file_name = 'data/htgroup';

my $lock_file_name = $user_data_dir_name . '.lock';

use Fcntl ':flock';
my $Lock;

sub lock_start () {
  return if $Lock;

  open $Lock, '>', $lock_file_name or die "$0: $lock_file_name: $!";
  flock $Lock, LOCK_EX;
} # lock_start

sub get_prop_hash ($) {
  my $user_prop_file_name = shift;

  return undef unless -f $user_prop_file_name;

  my $r = {};
  
  open my $user_prop_file, '<:encoding(utf8)', $user_prop_file_name
      or die "$0: $user_prop_file_name: $!";
  while (<$user_prop_file>) {
    tr/\x0D\x0A//d;
    my ($n, $v) = split /:/, $_, 2;
    if ($n =~ s/^\@//) {
      push @{$r->{$n} ||= []}, $v // '';
    } elsif ($n =~ s/^%//) {
      $r->{$n}->{$v // ''} = 1;
    } else {
      $n =~ s/^\$//;
      $r->{$n} = $v // '';
    }
  }
  
  return $r;
} # get_prop_hash

sub set_prop_hash ($$) {
  my $user_prop_file_name = shift;;
  my $prop = shift;
  
  my $has_file = -f $user_prop_file_name;
  
  open my $user_prop_file, '>:encoding(utf8)', $user_prop_file_name
      or die "$0: $user_prop_file_name: $!";
  for my $prop_name (sort {$a cmp $b} keys %$prop) {
    if (ref $prop->{$prop_name} eq 'ARRAY') {
      my $v = '@' . $prop_name;
      $v =~ tr/\x0D\x0A://d;
      for (@{$prop->{$prop_name}}) {
        my $pv = $_;
        $pv =~ tr/\x0D\x0A/  /;
        print $user_prop_file $v . ':' . $pv . "\x0A";
      }
    } elsif (ref $prop->{$prop_name} eq 'HASH') {
      my $v = '%' . $prop_name;
      $v =~ tr/\x0D\x0A://d;
      for (sort {$a cmp $b} keys %{$prop->{$prop_name}}) {
        next unless $prop->{$prop_name}->{$_};
        my $pv = $_;
        $pv =~ tr/\x0D\x0A/  /;
        print $user_prop_file $v . ':' . $pv . "\x0A";
      }
    } else {
      my $v = '$' . $prop_name;
      $v =~ tr/\x0D\x0A://d;
      my $pv = $prop->{$prop_name};
      $pv =~ tr/\x0D\x0A/  /;
      print $user_prop_file $v . ':' . $pv . "\x0A";
    }
  }
  close $user_prop_file_name;

  system_ ('cvs', 'add', $user_prop_file_name) unless $has_file;
} # set_prop_hash

sub commit ($) {
  my $msg = shift // $0;
  system_ ('cvs', 'commit', -m => $msg, $user_data_dir_name);
} # commit

sub get_user_prop ($) {
  my $user_id = shift;
  return get_prop_hash ($user_data_dir_name . $user_id . $user_prop_file_suffix);
} # get_user_prop

sub set_user_prop ($$) {
  my ($user_id, $prop) = @_;
  return set_prop_hash ($user_data_dir_name . $user_id . $user_prop_file_suffix,
                        $prop);
} # set_user_prop

sub get_group_prop ($) {
  my $group_id = shift;
  return get_prop_hash ($group_data_dir_name .
                        $group_id . $group_prop_file_suffix);
} # get_group_prop

sub set_group_prop ($$) {
  my ($group_id, $prop) = @_;
  return set_prop_hash ($group_data_dir_name .
                        $group_id . $group_prop_file_suffix,
                        $prop);
} # set_group_prop

sub get_all_users () {
  my @r;
  opendir my $user_data_dir, $user_data_dir_name;
  for (readdir $user_data_dir) {
    if (/^([0-9a-z-]+)\Q$user_prop_file_suffix\E$/) {
      push @r, $1;
    }
  }
  return @r;
} # get_all_users

sub get_all_groups () {
  my @r;
  opendir my $group_data_dir, $group_data_dir_name;
  for (readdir $group_data_dir) {
    if (/^([0-9a-z-]+)\Q$group_prop_file_suffix\E$/) {
      push @r, $1;
    }
  }
  return @r;
} # get_all_groups

sub regenerate_htpasswd_and_htgroup () {
  my %htpasswd;
  my %htgroup;
  
  my @group = get_all_groups ();
  
  for my $user_id (get_all_users ()) {
    my $user_prop = get_user_prop ($user_id);
    next if $user_prop->{disabled};
    next unless $user_prop->{pass_crypted};

    $htpasswd{$user_id} = $user_prop->{pass_crypted};

    for (@group) {
      if ($user_prop->{'group.' . $_}->{member}) {
        $htgroup{$_}->{$user_id} = 1;
      }
    }
  }

  open my $file, '>', $htpasswd_file_name or die "$0: $htpasswd_file_name: $!";
  for (sort {$a cmp $b} keys %htpasswd) {
    print $file $_, ':', $htpasswd{$_}, "\x0A";
  }
  
  open my $file, '>', $htgroup_file_name or die "$0: $htgroup_file_name: $!";
  for my $group_id (sort {$a cmp $b} keys %htgroup) {
    print $file $group_id, ': ',
        join ' ', sort {$a cmp $b} keys %{$htgroup{$group_id}};
    print $file "\x0A";
  }
} # regenerate_htpasswd_and_htgroup

sub print_error ($$;$) {
  my ($code, $text, $text_arg) = @_;
  our $Lang;
  binmode STDOUT, ':encoding(utf-8)';
  my $_text = $text;
  $_text =~ s/%s/$text_arg/g;
  print qq[Status: $code $_text
Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang="$Lang">
<title lang=en>$code @{[htescape ($_text)]}</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>];
  print_text ('Error');
  print q[</h1><p>];
  print_text ($text, sub { print '', htescape ($text_arg) });
  print_text ('.');
  print q[<!--];
  print 0 for 0..511; # for WinIE
  print q[-->];
} # print_error

sub check_password ($) {
  my $cgi = shift;

  my $user_pass = $cgi->get_parameter ('user-pass');
  my $user_pass2 = $cgi->get_parameter ('user-pass2');
  if ($user_pass ne $user_pass2) {
    print_error (400, 'Two passwords you input are different');
    exit;
  }
    
  if (4 > length $user_pass) {
    print_error (400, 'Password must be longer than 3 characters');
    exit;
  }

  my $pass_crypted = crypt $user_pass,
      join '', (0..9, 'A'..'Z', 'a'..'z')[rand 64, rand 64];
  return $pass_crypted;
} # check_password

sub send_mail ($$) {
  require Net::SMTP;
  require Encode;
  
  my $smtp = Net::SMTP->new ('localhost');
  $smtp->mail ($mail_from);
  $smtp->to ($mail_to);
  ## NOTE: What's wrong with UTF-8 Subject? :-)
  $smtp->data (Encode::encode ('utf-8', "From: <$mail_from>
To: <$mail_to>
Subject: $_[0]
Content-Type: text/plain; charset=utf-8
MIME-Version: 1.0

$_[1]"));
  $smtp->send;
} # send_mail

sub system_ (@) {
  (system join (' ', map {quotemeta $_} @_) . " > /dev/null") == 0
      or die "$0: $?";
} # system_

sub htescape ($) {
  my $s = shift;
  $s =~ s/&/&amp;/g;
  $s =~ s/</&lt;/g;
  $s =~ s/>/&gt;/g;
  $s =~ s/"/&quot;/g;
  return $s;
} # htescape

1;
