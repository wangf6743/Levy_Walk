%% Plot simulation mental_r spectra
% One alpha one color, all spectra on one figure

clc; clear; close all; tic;

%% =========================
% Path settings
% =========================

% the folder where the simulation data are stored
dataDir = '/Users/wang/Desktop/levy_walk/original_project/experiment/spectra/mental_simulation';

figSaveDir = fullfile(dataDir, 'figures');
if ~exist(figSaveDir, 'dir')
    mkdir(figSaveDir);
end

%% =========================
% Parameters
% =========================

trialnumber = 40;

alphaRows = 0:10;
alphaValues = alphaRows / 10;

params.Fs = 1000;
params.fpass = [0 500];
params.tapers = [10 19];
params.trialave = 1;

p = 0.05;
params.err = [1 p];

%% =========================
% Colormap: viridis if available
% =========================

if exist('viridis', 'file') == 2
    cmap = viridis(256);
else
    cmap = parula(256);
end

%% =========================
% Figure settings
% =========================

fontName = 'Arial';
fontSize = 10;

fig = figure('Units', 'inches', ...
             'Position', [1 1 2.8 2], ...
             'PaperUnits', 'inches', ...
             'PaperPosition', [0 0 2.8 2], ...
             'PaperSize', [2.8 2], ...
             'Color', 'w');

hold on;

lineCount = 0;

%% =========================
% Read CSVs and plot spectra
% =========================

for trial = 40:trialnumber

    csvName = sprintf('trial_%02d_last_half_mental_r_by_alpha.csv', trial);
    csvPath = fullfile(dataDir, csvName);

    if ~exist(csvPath, 'file')
        fprintf('Missing file: %s\n', csvPath);
        continue;
    end

    T = readtable(csvPath);

    for ia = 1:numel(alphaRows)

        alphaRow = alphaRows(ia);
        alphaValue = alphaValues(ia);

        idx = T.alpha == alphaRow;

        if ~any(idx)
            fprintf('Missing alpha row %d in trial %02d\n', alphaRow, trial);
            continue;
        end

        % 去掉第一列 alpha，只取 mental_r_1, mental_r_2, ...
        x = table2array(T(idx, 2:end));
        x = x(:);

        % 去掉 NaN / Inf
        x = x(isfinite(x));

        if numel(x) < 2
            fprintf('Too few valid samples: trial %02d, alpha %.1f\n', trial, alphaValue);
            continue;
        end

        % 和你真实数据保持一致：去均值 + detrend
        x = x - mean(x);
        x = dtrend(x);

        data = x(:);

        % Multitaper spectrum
        [S, f] = mtspectrumc(data, params);

        % 转成 dB
        y = 10 * log10(S);

        % alpha 对应颜色
        colorIdx = round(alphaValue * 255) + 1;
        colorIdx = max(1, min(256, colorIdx));
        thisColor = cmap(colorIdx, :);

        plot(f, y, ...
            'Color', thisColor, ...
            'LineWidth', 0.4);

        lineCount = lineCount + 1;
    end
end

hold off;

fprintf('Plotted %d spectra.\n', lineCount);

%% =========================
% Figure style
% =========================

xlim([0 500]);
ylim([-160 -30]);

xlabel('Frequency (Hz)', ...
    'FontName', fontName, ...
    'FontSize', fontSize);

ylabel('Power (dB)', ...
    'FontName', fontName, ...
    'FontSize', fontSize);

set(gca, ...
    'FontName', fontName, ...
    'FontSize', fontSize, ...
    'LineWidth', 0.8, ...
    'TickDir', 'out', ...
    'Box', 'off');

%% =========================
% Colorbar for alpha
% =========================

colormap(cmap);
clim([0 1]);

cb = colorbar;
cb.Label.String = '\alpha';
cb.Label.FontName = fontName;
cb.Label.FontSize = fontSize;
cb.FontName = fontName;
cb.FontSize = fontSize;
cb.Ticks = 0:0.2:1;
cb.TickLabels = {'0.0','0.2','0.4','0.6','0.8','1.0'};
cb.Box = 'off';

%% =========================
% Save
% =========================

print(fig, fullfile(figSaveDir, 'simulation_mental_spectra_all_alpha.svg'), ...
    '-dsvg', '-painters');

print(fig, fullfile(figSaveDir, 'simulation_mental_spectra_all_alpha.png'), ...
    '-dpng', '-r600');

toc;