%% Plot mental_r for trial 40, one alpha per figure

clc; clear; close all;

%% =========================
% Path settings
% =========================


% the folder where the simulation data are stored
dataDir = '/Users/wang/Desktop/levy_walk/original_project/experiment/spectra/mental_simulation';

outDir = fullfile(dataDir, 'figures');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

csvPath = fullfile(dataDir, 'trial_40_last_half_mental_r_by_alpha.csv');% Example trial

%% =========================
% Load CSV
% =========================

T = readtable(csvPath);
targetAlphaValues = [0.1, 0.7, 0.9];
alphaRows = round(targetAlphaValues * 10);

%% =========================
% Plot settings
% =========================

fontName = 'Arial';
fontSize = 10;
titleFontSize = 12;

%% =========================
% Plot one alpha per figure
% =========================

for i = 1:numel(alphaRows)

    alphaRow = alphaRows(i);
    alphaValue = targetAlphaValues(i);

    idx = T.alpha == alphaRow;

    if ~any(idx)
        fprintf('Missing alpha row: %d, true alpha = %.1f\n', alphaRow, alphaValue);
        continue;
    end


    values = table2array(T(idx, 2:end));
    values = values(:).';


    values = 4 * values(isfinite(values));

    if isempty(values)
        fprintf('No valid values for alpha = %.1f\n', alphaValue);
        continue;
    end

    t = 1:numel(values);
    lastN = numel(values);

    %% Create figure
    fig = figure('Units', 'inches', ...
                 'Position', [1 1 2.5 2.2], ...
                 'PaperUnits', 'inches', ...
                 'PaperPosition', [0 0 2.5 2.2], ...
                 'PaperSize', [2.5 2.2], ...
                 'Color', 'w');

    plot(t, values, ...
        'Color', 'k', ...
        'LineWidth', 0.5);

    %% Figure style

    title(sprintf('\\alpha = %.1f', alphaValue), ...
        'FontName', fontName, ...
        'FontSize', titleFontSize, ...
        'FontWeight', 'normal');

    xlabel('Time', ...
        'FontName', fontName, ...
        'FontSize', fontSize);

    ylabel('Mental representation (V_t)', ...
        'FontName', fontName, ...
        'FontSize', fontSize);

    set(gca, ...
        'FontName', fontName, ...
        'FontSize', fontSize, ...
        'LineWidth', 0.8, ...
        'TickDir', 'out', ...
        'Box', 'off');


    xlim([1 lastN]);
    xticks([1 lastN]);
    xticklabels({'start', 'end'});


    ylim([0 2]);

    %% Save

    alphaName = strrep(sprintf('%.1f', alphaValue), '.', 'p');

    print(fig, fullfile(outDir, ...
        sprintf('trial_40_mental_r_alpha_%s.svg', alphaName)), ...
        '-dsvg', '-painters');

    print(fig, fullfile(outDir, ...
        sprintf('trial_40_mental_r_alpha_%s.png', alphaName)), ...
        '-dpng', '-r600');

    close(fig);
end