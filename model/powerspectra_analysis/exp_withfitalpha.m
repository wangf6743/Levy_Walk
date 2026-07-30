% clear all;
% newdata without lingering
clc; clear; close all; tic;

%% Load dir

Cdir = '../data';
m_names = {
    Cdir,'dzpm0112201103';
    Cdir,'dzpm1409201102';
    Cdir,'dzpm1409201103';
    Cdir,'vehm0909201102';
    Cdir,'vehm2206201101';
    Cdir,'vehm2306201102';
    Cdir,'vehm2806201101';
    Cdir,'vehm0212201102';
    };
m_names1 = {
    Cdir,'DZP_1';
    Cdir,'DZP_2';
    Cdir,'DZP_3';
    Cdir,'VEH_1';
    Cdir,'VEH_2';
    Cdir,'VEH_3';
    Cdir,'VEH_4';
    Cdir,'VEH_5';
    };
%% Set parameters and variables

set(0,'defaultfigurecolor','w');
trialnumber = 8;
%% Manual alpha values, no fit_alpha
alpha_mouse = containers.Map();

alpha_mouse('dzpm0112201103') = 0.736531;
alpha_mouse('dzpm1409201102') = 0.744220;
alpha_mouse('dzpm1409201103') = 0.738820;

alpha_mouse('vehm0909201102') = 0.731269;
alpha_mouse('vehm2206201101') = 0.730166;
alpha_mouse('vehm2306201102') = 0.736973;
alpha_mouse('vehm2806201101') = 0.723653;
alpha_mouse('vehm0212201102') = 0.729793;

FIG = 0;
for period=3:3
for trial = 1:trialnumber
    if trial <= 3
        str1 = 'DZP_';
        str2 = num2str(trial);
    else
        str1 = 'VEH_';
        str2 = num2str(trial-4);
    end
    folderNow = m_names{trial,2};
    currFolder = [m_names{trial,1} '/' folderNow '/'];
    load([currFolder 'data_pos_ling_prog.mat'] , 'data_pos_ling_prog');
    path1 = data_pos_ling_prog(:,1:2);
    npath = size(path1,1);
    if period == 1
        path = path1;% whole
    else
        if period==3
            path = path1(floor(npath/2)+1:npath,:);%2nd path
        else
            path = path1(1:floor(npath/2),:);%1st path
        end
    end
    [rate, ~] = comput_traject_polar(path(:,1), path(:,2));
    ind = find(rate>=0.05);
    path = path(ind,:);
    data_without_linger = path;  
    x1 = data_without_linger(: , 1);
    y1 = data_without_linger(: , 2);
    [rate, Angle] = comput_traject_polar(x1 , y1);
    
    %% track
    original_x = data_pos_ling_prog(:,1);
    original_y = data_pos_ling_prog(:,2);
    num_end = numel(x1);  
    t1 = floor(num_end/2);
    num_end1 = size(original_x,1);
   
    t11 = floor(num_end1/2);

   %% compute information and risk
    % set parameter
    binsize = 2;
    epsilon2 = 0.218;
    input2 = [0 0];
    w2 = [(1-epsilon2) epsilon2 ;
        epsilon2 (1-epsilon2)];
    weight_Novelty = alpha_mouse(folderNow);
    
    % computation process
    % En=info,Ga=risk
    [Novelty , Security] = compute_occupancy(data_without_linger(:,1), data_without_linger(:,2) , binsize,path1);
    ndata = numel(Novelty);
    Output2 = zeros(ndata , 2, 'double');
    Mental_V = zeros(ndata , 1, 'double');
    for t = 1 : ndata
        output2 = w2*(sigmoid_SC(input2.' )) + [Novelty(t);Security(t)];%0-2
        Mental_V(t) = weight_Novelty*output2(1)+(1-weight_Novelty)*output2(2);
        Output2(t,:) = output2.';
        input2 = output2.';
    end
    mental(trial).Mental_V = Mental_V;
    mental(trial).Novelty = Novelty;
    mental(trial).Security = Security;
    
%     FIG = FIG + 1;
%     figure(kk)
%     subplot(1,3,3);
%     plot(Mental_V,'b');
%     xlim([0 ndata]);
%     ylim([0.1 0.5]);
%     hold on
%     plot(Mental_V(1:floor(ndata/2)),'r');
% 
%   
%     ylabel('Mental procation(r)','Fontsize',12);
%     xlabel('time','Fontsize',12);
% 
%     sgtitle(m_names1(kk,2), 'Interpreter','none');
end
    saveDir = fullfile('.', 'spectra');

    if ~exist(saveDir, 'dir')
        mkdir(saveDir);
    end
    
    if period == 1
        save(fullfile(saveDir, 'mental_procation.mat'), 'mental');
    else
        if period == 2
            save(fullfile(saveDir, 'mental_procation_1st.mat'), 'mental');
        else
            save(fullfile(saveDir, 'mental_procation_2nd.mat'), 'mental');
        end
    end
end


params.Fs=1000;
params.fpass=[0 500];
params.tapers=[10 19];
params.trialave=1;
p=0.05;
params.err=[1 p];

for trial =1:8
    data = [];
    x= mental(trial).Mental_V.';
    x = (x - mean(x));
    x =dtrend(x);
    data = x.';
    
    [S,f,Serr] = mtspectrumc(data,params);
    spectra(trial).Power = S;
    spectra(trial).fre = f;
    % spectra(control_parameter).R = R;
    spectra(trial).Serr = Serr;
end



%% =========================
%  Plot settings
% =========================

% GROUP_COLORS = {
%     "DZP": "#0072B2",
%     "VEH": "#D55E00",
% }

color_DZP = [0 114 178] / 255;   % #0072B2
color_VEH = [213 94 0] / 255;    % #D55E00

fontName = 'Arial';
fontSize = 10;
titleFontSize = 12;

figSaveDir = fullfile('.', 'figures');
if ~exist(figSaveDir, 'dir')
    mkdir(figSaveDir);
end

mentalSaveDir = fullfile(figSaveDir, 'mental_single_mouse');
if ~exist(mentalSaveDir, 'dir')
    mkdir(mentalSaveDir);
end


%% =========================
%  1. Plot spectra together
% =========================

fig2 = figure(2);
clf;
set(fig2, ...
    'Units', 'inches', ...
    'Position', [1 1 2.3 2], ...
    'PaperUnits', 'inches', ...
    'PaperPosition', [0 0 2.3 2], ...
    'PaperSize', [2.3 2], ...
    'Color', 'w');

hold on;

h_DZP = [];
h_VEH = [];

for trial = 1:8
    x = spectra(trial).fre;
    y = 10*log10(spectra(trial).Power);

    if trial <= 3
        h = plot(x, y, ...
            'Color', color_DZP, ...
            'LineWidth', 0.4);
        if isempty(h_DZP)
            h_DZP = h;
        end
    else
        h = plot(x, y, ...
            'Color', color_VEH, ...
            'LineWidth', 0.4);
        if isempty(h_VEH)
            h_VEH = h;
        end
    end
end

hold off;

xlim([0 500]);
ylim([-150 -30]);

xlabel('Frequency (Hz)', ...
    'FontName', fontName, ...
    'FontSize', fontSize);

ylabel('Power (dB)', ...
    'FontName', fontName, ...
    'FontSize', fontSize);

legend([h_DZP h_VEH], {'DZP', 'VEH'}, ...
    'Box', 'off', ...
    'FontName', fontName, ...
    'FontSize', fontSize, ...
    'Location', 'best');

set(gca, ...
    'FontName', fontName, ...
    'FontSize', fontSize, ...
    'LineWidth', 0.1, ...
    'TickDir', 'out', ...
    'Box', 'off');

print(fig2, fullfile(figSaveDir, 'mental_spectra_overlay.svg'), '-dsvg', '-painters');
print(fig2, fullfile(figSaveDir, 'mental_spectra_overlay.png'), '-dpng', '-r600');


%% =========================
%  2. Plot Mental representation for each mouse
% =========================

for trial = 1:8

    folderNow = m_names{trial,2};
    mouseLabel = m_names1{trial,2};

    Mental_V = mental(trial).Mental_V;
    ndata = numel(Mental_V);

    alpha_now = alpha_mouse(folderNow);

    if trial <= 3
        groupLabel = 'DZP';
        groupColor = color_DZP;
    else
        groupLabel = 'VEH';
        groupColor = color_VEH;
    end

    fig = figure('Units', 'inches', ...
                 'Position', [1 1 2.5 2.2], ...
                 'PaperUnits', 'inches', ...
                 'PaperPosition', [0 0 2.5 2.2], ...
                 'PaperSize', [2.5 2.2], ...
                 'Color', 'w');

    plot(Mental_V, ...
        'Color', 'k', ...
        'LineWidth', 0.1);

    xlim([1 ndata]);

    xlabel('', 'FontName', fontName, 'FontSize', fontSize);

    ylabel('Mental representation (V_t)', ...
        'FontName', fontName, ...
        'FontSize', fontSize);

    title(groupLabel, ...
        'FontName', fontName, ...
        'FontSize', titleFontSize, ...
        'FontWeight', 'normal');

    set(gca, ...
        'FontName', fontName, ...
        'FontSize', fontSize, ...
        'LineWidth', 0.8, ...
        'TickDir', 'out', ...
        'Box', 'off');


    xticks([1 ndata]);
    xticklabels({'start', 'end'});


    yl = ylim;
    xl = xlim;

    text(xl(1) + 0.05*(xl(2)-xl(1)), ...
         yl(1) + 0.08*(yl(2)-yl(1)), ...
         sprintf('\\alpha = %.4f', alpha_now), ...
         'FontName', fontName, ...
         'FontSize', fontSize, ...
         'Interpreter', 'tex');


    outName = sprintf('%s_mental_representation', mouseLabel);

    print(fig, fullfile(mentalSaveDir, [outName '.svg']), '-dsvg', '-painters');
    print(fig, fullfile(mentalSaveDir, [outName '.png']), '-dpng', '-r600');

    close(fig);
end