
clear
close all

% Cdir1='G:\EMBL work\Emergence_test_NL\emergence_june2011';
% Cdir2='G:\EMBL work\Emergence_test_NL\Emergence_sep2011';
% Cdir3='G:\EMBL work\Emergence_test_NL\Emergence_Dec2011';
% Cdir4='G:\EMBL work\Emergence_test_NL\Emergence_Feb2012';

%I:\EMBL work\Emergence_test_NL\Emergence_Dec2011
% Cdir1='F:\EMBL work\Emergence_test_NL\emergence_june2011';
% Cdir2='F:\EMBL work\Emergence_test_NL\Emergence_sep2011';
% Cdir3='F:\EMBL work\Emergence_test_NL\Emergence_Dec2011';
% Cdir4='F:\EMBL work\Emergence_test_NL\Emergence_Feb2012';
Cdir1='D:\emergence test\emergence_june2011';
Cdir2='D:\emergence test\Emergence_sep2011';
Cdir3='D:\emergence test\Emergence_Dec2011';
Cdir4='D:\emergence test\Emergence_Feb2012';

% % files with full buildup behaviour
m_names ={       
Cdir1,'m2206201101',0;
Cdir1,'m2306201102',0; 
Cdir1,'m2806201101',0;
Cdir2,'m0909201102' ,0;  % veh
Cdir4,'m0712201103' ,0;  % veh
Cdir3,'m0212201102' ,0;  % veh
Cdir2,'m1409201102' ,1;  % dzp
Cdir2,'m1409201103' ,1;  % dzp
Cdir3,'m0112201102' ,1;  % dzp
Cdir3,'m0112201103' ,1;  % dzp
}; 

%  % files with not full buildup behaviour, but out garden
%  m_names ={         
% Cdir2,'m1509201103' ,1;  % dzp
% %Cdir2,'m2009201101' ,1;  % dzp % no eeg
% 
% Cdir3,'m0112201101' ,0;  % veh 
% %Cdir3,'m0212201101' ,0;  % veh  % no eeg
% %Cdir3,'m0212201101' ,0;  % veh  % no eeg
% %Cdir4,'m0412201101' ,1;  % dzp  % no eeg
% %Cdir4,'m0412201102' ,0;  % veh  % no eeg
% Cdir4,'m0512201101' ,0;  % veh  % no ir channel
% Cdir4,'m0712201102' ,1;  % dzp
% Cdir4,'m0712201103' ,0;  % veh
% Cdir3,'m0112201102' ,1;  % dzp
% };  


% files with garden activiy and home only activity
 m_names ={     
% %  Cdir2,'m0909201101' ,1;  % dzp  % data not full
%   Cdir2,'m1209201101' ,0;  % veh
% % Cdir2,'m1309201101' ,1;  % dzp   %%%
%  Cdir2,'m1309201102' ,1;  % veh
%  Cdir2,'m1409201101' ,0;  % veh
%   Cdir2,'m1509201101' ,0;  % veh
%   Cdir2,'m1509201102' ,0;  % veh
%   Cdir2,'m1609201101' ,1;  % dzp
%   Cdir2,'m1609201102' ,0;  % veh
%   Cdir2,'m1709201101' ,0;  % veh
%   Cdir2,'m1709201102' ,1;  % dzp
%  Cdir2,'m2009201102' ,0;  % veh
%  Cdir2,'m2207201101' ,0;  % veh
%   Cdir4,'m0512201102' ,1;  % dzp
%   Cdir4,'m0612201101' ,1;  % dzp  
%  % Cdir4,'m0612201102' ,0;  % veh  % only a litte data, data not full
%  % Cdir4,'m0612201103' ,0;  % veh  % only 10 mins data, data not full
%   Cdir4,'m0712201101' ,1;  % dzp
%  };

folderNum=length(m_names);


saveDir='D:\emergence test\tracks_for_Bailu_20260504';

for kk=1:folderNum
%for kk=1:1    
    
    clear data_80min data_m15min data_pos_ling_prog path_segment all_index3;
    clear lingseg_index1 progseg_index1 homeseg_index1 ndata;
    file1='';
    folderNow=m_names{kk,2};
    currFolder=[m_names{kk,1} '\' folderNow '\'];

   % load([currFolder 'data_80min.mat']);
   % load([currFolder 'data_b10min.mat']);
   % load([currFolder 'data_m15min.mat']);
   % load([currFolder 'path_segment.mat']);
    load([currFolder 'data_pos_ling_prog.mat']);
    load([currFolder 'data_arena.mat']);
 %   load([currFolder 'data_angletheta.mat']);

    path = 'C:\myfolder\data';
    filename = fullfile(saveDir, ['data_track_' folderNow '.mat']);
    save(filename, 'data_pos_ling_prog','xy_arena','xy_center');
end






