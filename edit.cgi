#!/usr/bin/perl
use strict;

use lib qw[/home/httpd/html/www/markup/html/whatpm
           /home/wakaba/work/manakai2/lib];

use CGI::Carp qw[fatalsToBrowser];
require Message::CGI::Carp;

require 'users.pl';

require Message::CGI::HTTP;
require Encode;
my $cgi = Message::CGI::HTTP->new;
$cgi->{decoder}->{'#default'} = sub {
  return Encode::decode ('utf-8', $_[1]);
};

require Message::DOM::DOMImplementation;
my $dom = Message::DOM::DOMImplementation->new;

my $path = $cgi->path_info;
$path = '' unless defined $path;

my @path = split m#/#, percent_decode ($path), -1;
shift @path;

if (@path == 3 and
    $path[0] eq 'users' and
    $path[1] =~ /\A[0-9a-z-]+\z/) {
  my $user_id = $path[1];
  my $ac = check_access_right (allowed_users => {$user_id => 1},
                               allowed_groups => {'admin-users' => 1});

  if ($path[2] eq '') {
    my $user_prop = get_user_prop ($user_id);
    if ($user_prop) {
      binmode STDOUT, ':encoding(utf-8)';
      
      my $e_user_id = htescape ($user_id);
      
      print qq[Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>User $e_user_id</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>User $e_user_id</h1>
];

      my @joined;
      my @requested;
      my @invited;
      my @can_join;
      my @can_request;
      for my $group_id (get_all_groups ()) {
        my $gs = $user_prop->{'group.' . $group_id};
        if ($gs->{member}) {
          push @joined, $group_id;
        } elsif ($gs->{no_approval}) {
          push @requested, $group_id;
        } elsif ($gs->{invited}) {
          push @invited, $group_id;
        } else {
          my $group_prop = get_group_prop ($group_id);
          if ($group_prop->{join_condition}->{invitation}) {
            #
          } elsif ($group_prop->{join_condition}->{approval}) {
            push @can_request, $group_id;
          } else {
            push @can_join, $group_id;
          }
        }
      }

      print qq[<section id=groups><h2>Groups</h2>];
      
      if (@joined) {
        print_list_section
            (id => 'groups-joined',
             title => 'Groups you have joined',
             items => \@joined,
             print_item => sub {
               my $group_id = shift;
               print q[<form action="group.] . htescape ($group_id);
               print q[" accept-charset=utf-8 method=post>];
               print q[<a href="../../groups/].htescape ($group_id) . '/';
               print q[">] . htescape ($group_id), q[</a> ];
               print q[<input type=hidden name=action value=leave>];
               print q[<input type=submit value="Leave this group"></form>];
             });
      }
      
      if (@requested) {
        print_list_section
            (id => 'groups-requested',
             title => 'Groups you have requested to join but not approved yet',
             items => \@requested,
             print_item => sub {
               my $group_id = shift;
               print q[<form action="group.] . htescape ($group_id);
               print q[" accept-charset=utf-8 method=post>];
               print q[<a href="../../groups/].htescape ($group_id) . '/';
               print q[">] . htescape ($group_id), q[</a> ];
               print q[<input type=hidden name=action value=leave>];
               print q[<input type=submit value="Cancel the request"></form>];
             });
      }
      
      if (@invited) {
        print_list_section
            (id => 'groups-invited',
             title => 'Groups you have been invited but not joined yet, or you have left',
             items => \@invited,
             print_item => sub {
               my $group_id = shift;
               print q[<form action="group.] . htescape ($group_id);
               print q[" accept-charset=utf-8 method=post>];
               print q[<a href="../../groups/].htescape ($group_id) . '/';
               print q[">] . htescape ($group_id), q[</a> ];
               print q[<input type=hidden name=action value=join>];
               print q[<input type=submit value="Join this group"></form>];
             });
      }
      
      if (@can_join) {
        print_list_section
            (id => 'groups-can-join',
             title => 'Groups you can join now (without approval)',
             items => \@can_join,
             print_item => sub {
               my $group_id = shift;
               print q[<form action="group.] . htescape ($group_id);
               print q[" accept-charset=utf-8 method=post>];
               print q[<a href="../../groups/].htescape ($group_id) . '/';
               print q[">] . htescape ($group_id), q[</a>];
               print q[<input type=hidden name=action value=join>];
               print q[<input type=submit value="Join this group"></form>];
             });
      }
      
      if (@can_request) {
        print_list_section
            (id => 'groups-can-request',
             title => 'Groups you can request to join (approval required to join)',
             items => \@can_request,
             print_item => sub {
               my $group_id = shift;
               print q[<form action="group.] . htescape ($group_id);
               print q[" accept-charset=utf-8 method=post>];
               print q[<a href="../../groups/].htescape ($group_id) . '/';
               print q[">] . htescape ($group_id), q[</a> ];
               print q[<input type=hidden name=action value=join>];
               print q[<input type=submit value="Join this group"></form>];
             });
      }
      
      print q[</section><section id=props><h2>Properties</h2>

<p><em>Though these properties are only accessible to administrators,
you are advised not to expose any confidential data.</em>];

      print_prop_list ($ac, $user_prop,
        {
          name => 'full_name',
          label => 'Full name',
          field_type => 'text',
        },
        {
          name => 'mail_addr',
          label => 'Mail address',
          field_type => 'email',
        },
        {
          name => 'home_url',
          label => 'Web site URL',
          field_type => 'url',
        },
      );

      print qq[</section><section id=password>
<h2>Password</h2>

<form action=password method=post accept-charset=utf-8>

<p>You can change the password.

<p><strong>New password</strong>: <input type=password name=user-pass
size=10 required pattern=".{4,}" title="Type 4 characters at minimum">

<p><strong>New password</strong> (type again): <input type=password
name=user-pass2 size=10 required pattern=".{4,}">

<p><input type=submit value=Change>

</form>
</section>

<section id=disable-account><h2>Disable account</h2>

<form action=disabled method=post accept-charset=utf-8>

<p><label><input type=checkbox name=action value=enable
@{[$user_prop->{disabled} ? '' : 'checked']}> Enable this
account.</label>

<p><strong>Caution!</strong> Once you disable your own account, you
cannot enable your account by yourself.

<p><input type=submit value=Change>

</form>

</section>];

      exit;
    }
  } elsif ($path[2] =~ /\Agroup\.([0-9a-z-]+)\z/) {
    my $group_id = $1;
    if ($cgi->request_method eq 'POST') {
      lock_start ();
      binmode STDOUT, ':encoding(utf-8)';

      my $user_prop = get_user_prop ($user_id);
      my $group_prop = get_group_prop ($group_id);
      
      if ($user_prop and $group_prop) {
        my $gs = ($user_prop->{'group.' . $group_id} ||= {});
        
        my $action = $cgi->get_parameter ('action');
        my $status;
        if ($action eq 'join') {
          if (scalar $cgi->get_parameter ('agreed')) {
            if ($gs->{member}) {
              $status = q[You are a member];
              #
            } elsif ($gs->{no_approval}) {
              $status = q[You are waiting for an approval];
              #
            } elsif ($gs->{invited}) {
              $gs->{member} = 1;
              $status = q[Registered];
              #
            } else {
              if ($group_prop->{join_condition}->{invitation}) {
                print_error (403, 'You are not invited to this group');
                exit;
              } elsif ($group_prop->{join_condition}->{approval}) {
                $gs->{no_approval} = 1;
                $status = q[Request submitted];
                #
              } else {
                $gs->{member} = 1;
                $status = q[Registered];
                #
              }
            }
          } else {
            my $e_group_id = htescape ($group_id);
            print qq[Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>Joining the group $e_group_id</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>Joining the group $e_group_id</h1>

<dl>
<dt>Description
<dd>@{[$group_prop->{desc}]}
</dl>

<form action="@{[htescape ($cgi->request_uri)]}" accept-charset=utf-8 method=post>
<input type=hidden name=action value=join>

<p>Do you really want to join this group?
<input type=submit name=agreed value=yes>
<input type=button value=no onclick="history.back ()">

</form>];
            exit;
          }
        } elsif ($action eq 'leave') {
          if ($gs->{member}) {
            delete $gs->{member};
            $gs->{invited} = 1;
            $status = 'Unregistered';
            #
          } elsif ($gs->{no_approval}) {
            delete $gs->{no_approval};
            delete $gs->{invited};
            $status = 'Request canceled';
            #
          } else {
            $status = 'You are not a member';
            #
          }
        } else {
          print_error (400, 'Bad action parameter');
          exit;
        }

        set_user_prop ($user_id, $user_prop);
        regenerate_htpasswd_and_htgroup ();
        commit ();

        redirect (303, $status, './');
        exit;
      }
    }
  } elsif ($path[2] eq 'password') {
    if ($cgi->request_method eq 'POST') {
      lock_start ();
      binmode STDOUT, ':encoding(utf-8)';
      
      my $user_prop = get_user_prop ($user_id);

      if ($user_prop) {
        $user_prop->{pass_crypted} = check_password ($cgi);
        
        set_user_prop ($user_id, $user_prop);
        regenerate_htpasswd_and_htgroup ();
        commit ();
        
        ## Browsers do not support 205.
        #print qq[Status: 205 Password changed\n\n];
        print qq[Status: 204 Password changed\n\n];
        exit;
      }
    }
  } elsif ($path[2] eq 'disabled') {
    if ($cgi->request_method eq 'POST') {
      lock_start ();
      binmode STDOUT, ':encoding(utf-8)';
      
      my $user_prop = get_user_prop ($user_id);

      if ($user_prop) {
        my $action = $cgi->get_parameter ('action');
        if (defined $action and $action eq 'enable') {
          delete $user_prop->{disabled};
        } else {
          $user_prop->{disabled} = 1;
        }

        set_user_prop ($user_id, $user_prop);
        regenerate_htpasswd_and_htgroup ();
        commit ();

        print "Status: 204 Property updated\n\n";
        exit;
      }
    }
  } elsif ($path[2] eq 'prop') {
    if ($cgi->request_method eq 'POST') {
      lock_start ();
      my $user_prop = get_user_prop ($user_id);
      if ($user_prop) {
        binmode STDOUT, ':encoding(utf-8)';

        my $prop_name = $cgi->get_parameter ('name');
        if (defined $prop_name and
            {
              full_name => 1,
              mail_addr => 1,
              home_url => 1,
            }->{$prop_name}) {
          $user_prop->{$prop_name} = $cgi->get_parameter ('value');

          set_user_prop ($user_id, $user_prop);
          commit ();
          
          print "Status: 204 Property updated\n\n";
          exit;
        } else {
          print_error (400, 'Bad property');
          exit;
        }
      }
    }
  }
} elsif (@path == 3 and
         $path[0] eq 'groups' and
         $path[1] =~ /\A[0-9a-z-]+\z/) {
  my $group_id = $path[1];
  my $ac = check_access_right (allowed_groups => {'admin-groups' => 1},
                               group_context => $group_id);

  if ($path[2] eq '') {
    my $group_prop = get_group_prop ($group_id);
    if ($group_prop) {
      binmode STDOUT, ':encoding(utf-8)';
      
      my $e_group_id = htescape ($group_id);
      
      print qq[Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>Group $e_group_id</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>Group $e_group_id</h1>];
      
      print q[<section id=props><h2>Properties</h2>];

      print_prop_list ($ac, $group_prop,
           {
            name => 'desc',
            label => 'Description',
            field_type => 'textarea',
            public => 1,
           },
           {
            name => 'admin_group',
            label => 'Administrative group',
            field_type => 'text',
           },
          );

      print q[</section><section id=members><h2>Members</h2>];

      if ($ac->{read_group_member_list}) {
        my @members;
        my @apps;
        my @invited;
        for my $user_id (get_all_users ()) {
          my $user_prop = get_user_prop ($user_id);
          my $gs = $user_prop->{'group.' . $group_id};
          if ($gs->{member}) {
            push @members, $user_id;
          } elsif ($gs->{no_approval}) {
            push @apps, $user_id;
          } elsif ($gs->{invited}) {
            push @invited, $user_id;
          }
        }
        
        if (@members) {
          print_list_section
              (id => 'formal-members',
               title => 'Formal members',
               items => \@members,
               print_item => sub {
                 my $user_id = shift;
                 print q[<form action="user.] . htescape ($user_id);
               print q[" accept-charset=utf-8 method=post>];
                 print qq[<a href="../../users/@{[htescape ($user_id)]}/">];
                 print '' . htescape ($user_id) . q[</a> ];
                 print q[<input type=hidden name=action value=unapprove>];
                 print q[<input type=submit value="Kick"></form>];
               });
        }
        
        if (@apps) {
          print_list_section
              (id => 'non-approved-users',
               title => 'Users who are waiting for the approval to join',
               items => \@apps,
               print_item => sub {
                 my $user_id = shift;
                 print q[<form action="user.] . htescape ($user_id);
                 print q[" accept-charset=utf-8 method=post>];
                 print qq[<a href="../../users/@{[htescape ($user_id)]}/">];
                 print '' . htescape ($user_id) . q[</a> ];
                 print q[<input type=hidden name=action value=approve>];
                 print q[<input type=submit value=Approve></form>];
               });
        }
        
        if (@invited) {
          print_list_section
              (id => 'invited-users',
               title => 'Users who are invited but not joined or are leaved',
               items => \@invited,
               print_item => sub {
                 my $user_id = shift;
                 print q[<form action="user.] . htescape ($user_id);
                 print q[" accept-charset=utf-8 method=post>];               
                 print qq[<a href="../../users/@{[htescape ($user_id)]}/">];
                 print '' . htescape ($user_id), q[</a> ];
                 print q[<input type=hidden name=action value=unapprove>];
                 print q[<input type=submit value="Cancel invitation"></form>];
               });
        }
      }

      my $join_condition = $group_prop->{join_condition};
      my $disabled = $ac->{write} ? '' : 'disabled';
      print qq[<section id=member-approval>
<h3>Member approval policy</h3>

<form action=join-condition method=post accept-charset=utf-8>

<p><label><input type=radio name=condition value=invitation $disabled
@{[$join_condition->{invitation} ? 'checked' : '']}> A user who is
invited by an administrator of the group can join the group.</label>

<p><label><input type=radio name=condition value=approval $disabled
@{[(not $join_condition->{invitation} and $join_condition->{approval})
?  'checked' : '']}> A user who is invited or approved by an
administrator of the group can join the group.</label>

<p><label><input type=radio name=condition value=anyone $disabled
@{[(not $join_condition->{invitation} and not
$join_condition->{approval}) ?  'checked' : '']}> Any user can join
the group.</label>

@{[$disabled ? '' : '<p><input type=submit value=Change>']}

</form>

</section>];

      if ($ac->{write}) {
        print q[<section id=member-invitation>
<h3>Invite a user</h3>

<form action=invite-user accept-charset=utf-8 method=post>

<p><strong>User id</strong>: <input type=text name=user-id
maxlength=20 size=10 required pattern="[0-9a-z-]{4,20}">

<p><input type=submit value=Invite>

</form>

</section>];
      }

      print q[</section>];

      exit;
    }
  } elsif ($path[2] eq 'join-condition') {
    forbidden () unless $ac->{write};

    if ($cgi->request_method eq 'POST') {
      lock_start ();
      my $group_prop = get_group_prop ($group_id);
      if ($group_prop) {
        binmode STDOUT, ':encoding(utf-8)';
        
        my $new_condition = $cgi->get_parameter ('condition');
        if ($new_condition eq 'invitation') {
          $group_prop->{join_condition}->{invitation} = 1;
          $group_prop->{join_condition}->{approval} = 1;
        } elsif ($new_condition eq 'approval') {
          $group_prop->{join_condition}->{approval} = 1;
          delete $group_prop->{join_condition}->{invitation};
        } else {
          delete $group_prop->{join_condition}->{invitation};
          delete $group_prop->{join_condition}->{approval};
        }

        set_group_prop ($group_id, $group_prop);
        commit ();
        
        print "Status: 204 join-condition property updated\n\n";
        exit;
      }
    }
  } elsif ($path[2] eq 'prop') {
    forbidden () unless $ac->{write};

    if ($cgi->request_method eq 'POST') {
      lock_start ();
      my $group_prop = get_group_prop ($group_id);
      if ($group_prop) {
        binmode STDOUT, ':encoding(utf-8)';

        my $prop_name = $cgi->get_parameter ('name');
        if (defined $prop_name and
            {desc => 1, admin_group => 1}->{$prop_name}) {
          $group_prop->{$prop_name} = $cgi->get_parameter ('value');

          set_group_prop ($group_id, $group_prop);
          commit ();
          
          print "Status: 204 Property updated\n\n";
          exit;
        } else {
          print_error (400, 'Bad property');
          exit;
        }
      }
    }
  } elsif ($path[2] =~ /\Auser\.([0-9a-z-]+)\z/ or
           $path[2] eq 'invite-user') {
    my $user_id = $1 // $cgi->get_parameter ('user-id') // '';
    if ($user_id =~ /\A[0-9a-z-]+\z/ and
        $cgi->request_method eq 'POST') {
      forbidden () unless $ac->{write};

      lock_start ();
      my $group_prop = get_group_prop ($group_id);
      my $user_prop = get_user_prop ($user_id);
      if ($group_prop and $user_prop) {
        binmode STDOUT, ':encoding(utf-8)';

        my $gs = ($user_prop->{'group.' . $group_id} ||= {});
        
        my $action = $cgi->get_parameter ('action');
        $action = 'approve' if $path[2] eq 'invite-user';
        my $status;
        if ($action eq 'approve') {
          if ($gs->{member}) {
            $status = 'He is a member';
            #
          } elsif ($gs->{no_approval}) {
            $gs->{member} = 1;
            delete $gs->{no_approval};
            $status = 'Registered';
            #
          } elsif ($gs->{invited}) {
            $status = 'He has been invited';
            #
          } else {
            $gs->{invited} = 1;
            $status = 'Invited';
            #
          }
        } elsif ($action eq 'unapprove') {
          if ($gs->{member}) {
            delete $gs->{member};
            delete $gs->{invited};
            $status = 'Unregistered';
            #
          } elsif ($gs->{invited}) {
            delete $gs->{invited};
            $status = 'Invitation canceled';
            #
          } else {
            $status = 'Not a member';
            #
          }
        } else {
          print_error (400, 'Bad action parameter');
          exit;
        }
        
        set_user_prop ($user_id, $user_prop);
        regenerate_htpasswd_and_htgroup ();
        commit ();
        
        print "Status: 204 $status\n\n";
        exit;
      }
    }
  }
} elsif (@path == 1 and $path[0] eq 'new-group') {
  check_access_right (allowed_groups => {'admin-groups' => 1});

  if ($cgi->request_method eq 'POST') {
    lock_start ();
    binmode STDOUT, ':encoding(utf-8)';
    
    my $group_id = $cgi->get_parameter ('group-id');

    if ($group_id !~ /\A[0-9a-z-]{4,20}\z/) {
      print_error (400, qq[Group id "$group_id" is invalid; use characters [0-9a-z-]{4,20}]);
      exit;
    }
    
    if (get_group_prop ($group_id)) {
      print_error (400, qq[Group id "$group_id" is already used]);
      exit;
    }

    my $group_prop = {id => $group_id};
    set_group_prop ($group_id, $group_prop);

    commit ();

    my $group_url = get_absolute_url ('groups/' . $group_id . '/');

    print qq[Status: 201 Group registered
Location: $group_url
Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>Group "@{[htescape ($group_id)]}" registered</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>Group "@{[htescape ($group_id)]}" registered</h1>
<p>The new group is created successfully.
<p>See <a href="@{[htescape ($group_url)]}">the group information page</a>.];
    exit;
  } else {
    binmode STDOUT, ":encoding(utf-8)";
    print qq[Content-Type: text/html; charset=utf-8

<!DOCTYPE HTML>
<html lang=en>
<title>Create a new group</title>
<link rel=stylesheet href="/www/style/html/xhtml">
<h1>Create a new group</h1>

<form action=new-group accept-charset=utf-8 method=post>

<p><strong>Group id</strong>: <input type=text name=group-id
maxlength=20 size=10 required pattern="[0-9a-z-]{4,20}"
title="Use a string of characters 'a'..'z', '0'..'9', and '-' with length 4..10 (inclusive)">

<p><input type=submit value=Create>

</form>];
    exit;
  }
} elsif (@path == 1 and $path[0] eq '') {
  my $user_id = $cgi->remote_user;
  forbidden () if not defined $user_id or $user_id !~ /\A[0-9a-z-]+\z/;

  redirect (303, 'See other', 'users/' . $user_id . '/');
  exit;
} elsif (@path == 0) {
  redirect (301, 'Moved', 'edit/');
  exit;
}

print_error (404, 'Not found');
exit;

sub print_list_section (%) {
  my %opt = @_;
  $opt{level} ||= 3;
  
  print q[<section id="] . htescape ($opt{id});
  print q["><h] . $opt{level} . q[>] . htescape ($opt{title});
  print q[</h] . $opt{level} . q[><ul>];
  for my $item (sort {$a cmp $b} @{$opt{items}}) {
    print q[<li>];
    $opt{print_item}->($item);
  }
  print q[</ul></section>];
} # print_list_section

sub print_prop_list ($$@) {
  my $ac = shift;
  my $prop_hash = shift;

  for my $prop (@_) {
    if ($prop->{public}) {
      print q[<p><strong>], htescape ($prop->{label}), q[</strong>: ];
      print $prop_hash->{$prop->{name}};
    }
    
    if ($ac->{write}) {
      print q[<form action="prop" accept-charset=utf-8 method=post>];
      print q[<input type=hidden name=name value="], htescape ($prop->{name}), q[">];
      if ($prop->{field_type} eq 'textarea') {
        print q[<p><label><strong>], htescape ($prop->{label});
        print q[</strong>: <br><textarea name="value"];
        print q[>], htescape ($prop_hash->{$prop->{name}} // '');
        print q[</textarea></label>];
        print q[<p><input type=submit value=Save>];
      } else {
        print q[<p><label><strong>], htescape ($prop->{label});
        print q[</strong>: <input type="] . $prop->{field_type};
        print q[" name="value" ];
        print q[value="], htescape ($prop_hash->{$prop->{name}} // '');
        print q["></label> ];
        print q[<input type=submit value=Save>];
      }
      print q[</form>];
    }
  }
} # print_prop_list

sub check_access_right (%) {
  my %opt = @_;
  
  my $user_id = $cgi->remote_user;
  forbidden () if not defined $user_id or $user_id !~ /\A[0-9a-z-]+\z/;
  
  my $user_prop = get_user_prop ($user_id);
  forbidden () unless $user_prop;

  my $ac = {};
  my $return_ac;

  if ($opt{allowed_users}->{$user_id}) {
    $ac->{write} = 1;
    $return_ac = 1;
  }

  for my $group_id (keys %{$opt{allowed_groups} or {}}) {
    my $group_prop = get_group_prop ($group_id);
    next unless $group_prop;
    
    my $gs = $user_prop->{'group.' . $group_id};
    if ($gs->{member}) {
      return {write => 1, read_group_member_list => 1};
    }
  }

  if (defined $opt{group_context}) {
    my $group_prop = get_group_prop ($opt{group_context});
    if ($group_prop) {
      if (defined $group_prop->{admin_group}) {
        my $ag_prop = get_group_prop ($group_prop->{admin_group});
        if ($ag_prop and
            $user_prop->{'group.' . $group_prop->{admin_group}}->{member}) {
          return {write => 1, read_group_member_list => 1};
        }
      }
      
      my $gs = $user_prop->{'group.' . $opt{group_context}};
      if ($gs->{member}) {
        $return_ac = 1;
      } elsif ($gs->{invited}) {
        $return_ac = 1;
      } elsif ($group_prop->{join_condition}->{acception}) {
        $return_ac = 1;
      } elsif (not $group_prop->{join_condition}->{invitation}) {
        $return_ac = 1;
      }
    }
  }
  
  return $ac if $return_ac;
  
  forbidden ();
} # check_access_right

sub forbidden () {
  my $user = $cgi->remote_user;
  if (defined $user) {
    print_error (403, q[Forbidden (you've logged in as ] . $user . ')');
  } else {
    print_error (403, 'Forbidden');
  }
  exit;
} # forbidden

sub redirect ($$$) {
  my ($code, $status, $url) = @_;
  
  my $abs_url = get_absolute_url ($url);

  print qq[Status: $code $status
Location: $abs_url
Content-Type: text/html; charset=us-ascii

See <a href="@{[htescape ($abs_url)]}">other page</a>.];
} # redirect

sub percent_decode ($) {
  return $dom->create_uri_reference ($_[0])
      ->get_iri_reference
      ->uri_reference;
} # percent_decode

sub get_absolute_url ($) {
  return $dom->create_uri_reference ($_[0])
      ->get_absolute_reference ($cgi->request_uri)
      ->get_iri_reference 
      ->uri_reference;
} # get_absolute_url
