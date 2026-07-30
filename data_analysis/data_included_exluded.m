% We calculated the explaortion time for each mouse

% To analyze the step-length distribution, we only included mice that explored outside
% the 40 cm home zone for more than 5 min.


clear all; clc;
data_dir = './all_data';
save_dir = fullfile(data_dir, 'trajectory_figures_grouped');
if ~exist(save_dir, 'dir')
    mkdir(save_dir);
end

% All the data
veh_ids = { ...
    'm2206201101', ...
    'm2306201102', ...
    'm2806201101', ...
    'm0909201102', ...
    'm0712201103', ...
    'm0212201102', ...
    'm0112201101', ...
    'm0512201101', ...
    'm1209201101', ...
    'm1309201102', ...
    'm1409201101', ...
    'm1509201101', ...
    'm1509201102', ...
    'm1609201102', ...
    'm1709201101', ...
    'm2009201102', ...
    'm2207201101' ...
    };

dzp_ids = { ...
    'm1409201102', ...
    'm1409201103', ...
    'm0112201102', ...
    'm0112201103', ...
    'm1509201103', ...
    'm0712201102', ...
    'm1609201101', ...
    'm1709201102', ...
    'm0512201102', ...
    'm0612201101', ...
    'm0712201101' ...
    };

files = dir(fullfile(data_dir, 'data_track_m*.mat'));

[~, idx] = sort({files.name});
files = files(idx);

nFiles = length(files);

if nFiles == 0
    error('No files found: %s', fullfile(data_dir, 'data_track_m*.mat'));
end


nCol = ceil(sqrt(nFiles));
nRow = ceil(nFiles / nCol);


mouse_id_list        = cell(nFiles, 1);
group_list           = cell(nFiles, 1);
outside_count_list   = nan(nFiles, 1);
outside_time_list    = nan(nFiles, 1);
outside_time_min_list = nan(nFiles, 1);
data_excluded_list   = false(nFiles, 1);

%% included data should >300s, the data would be excluded if the explaortioan time <300s 
veh_included = struct('mouse_id', {}, 'x', {}, 'y', {}, 'outside_time', {}, 'outside_time_min', {});
veh_excluded = struct('mouse_id', {}, 'x', {}, 'y', {}, 'outside_time', {}, 'outside_time_min', {});
dzp_included = struct('mouse_id', {}, 'x', {}, 'y', {}, 'outside_time', {}, 'outside_time_min', {});
dzp_excluded = struct('mouse_id', {}, 'x', {}, 'y', {}, 'outside_time', {}, 'outside_time_min', {});

veh_included_count = 0;
veh_excluded_count = 0;
dzp_included_count = 0;
dzp_excluded_count = 0;


%% Plot figure
orange_color = [0.90, 0.55, 0.20];
blue_color   = [0.20, 0.45, 0.85];

fig_all = figure('Visible', 'on', 'Color', 'w');
set(fig_all, 'Position', [100, 100, 1800, 1000]);

for i = 1:nFiles

    file_name = files(i).name;
    file_path = fullfile(data_dir, file_name);

    fprintf('Processing %s ...\n', file_name);


    S = load(file_path);

    var_names = fieldnames(S);
    track_data = [];

    for j = 1:length(var_names)
        temp = S.(var_names{j});
        if isnumeric(temp) && size(temp, 2) >= 2
            track_data = temp;
            break;
        end
    end

    if isempty(track_data)
        warning('No valid trajectory data found in %s', file_name);
        continue;
    end


    x = track_data(:, 1);
    y = track_data(:, 2);


    valid_idx = ~isnan(x) & ~isnan(y);
    x = x(valid_idx);
    y = y(valid_idx);

    if isempty(x) || isempty(y)
        warning('No valid x/y data found in %s', file_name);
        continue;
    end


    x0 = x(1);
    y0 = y(1);

    x = x - x0 + 100;
    y = y - y0 + 100;
    [~, name_no_ext, ~] = fileparts(file_name);
    mouse_id = erase(name_no_ext, 'data_track_');

    if ismember(mouse_id, veh_ids)
        group_name = 'veh';
    elseif ismember(mouse_id, dzp_ids)
        group_name = 'dzp';
    else
        group_name = 'unknown';
        warning('Mouse %s not found in veh_ids or dzp_ids. Marked as unknown.', mouse_id);
    end


    dist_from_start = sqrt((x - 100).^2 + (y - 100).^2);

    outside_idx = dist_from_start > 40;

    outside_count = sum(outside_idx);
    outside_time  = outside_count * 0.04;   % s
    outside_time_min = outside_time / 60;   % min

    % Test whether data should be excluded
    data_excluded = outside_time < 300;
    mouse_id_list{i}         = mouse_id;
    group_list{i}            = group_name;
    outside_count_list(i)    = outside_count;
    outside_time_list(i)     = outside_time;
    outside_time_min_list(i) = outside_time_min;
    data_excluded_list(i)    = data_excluded;

    if strcmp(group_name, 'veh')
        if data_excluded   % < 5 min
            veh_excluded_count = veh_excluded_count + 1;
            veh_excluded(veh_excluded_count).mouse_id = mouse_id;
            veh_excluded(veh_excluded_count).x = x;
            veh_excluded(veh_excluded_count).y = y;
            veh_excluded(veh_excluded_count).outside_time = outside_time;
            veh_excluded(veh_excluded_count).outside_time_min = outside_time_min;
        else               % >= 5 min
            veh_included_count = veh_included_count + 1;
            veh_included(veh_included_count).mouse_id = mouse_id;
            veh_included(veh_included_count).x = x;
            veh_included(veh_included_count).y = y;
            veh_included(veh_included_count).outside_time = outside_time;
            veh_included(veh_included_count).outside_time_min = outside_time_min;
        end
    
    elseif strcmp(group_name, 'dzp')
        if data_excluded   % < 5 min
            dzp_excluded_count = dzp_excluded_count + 1;
            dzp_excluded(dzp_excluded_count).mouse_id = mouse_id;
            dzp_excluded(dzp_excluded_count).x = x;
            dzp_excluded(dzp_excluded_count).y = y;
            dzp_excluded(dzp_excluded_count).outside_time = outside_time;
            dzp_excluded(dzp_excluded_count).outside_time_min = outside_time_min;
        else               % >= 5 min
            dzp_included_count = dzp_included_count + 1;
            dzp_included(dzp_included_count).mouse_id = mouse_id;
            dzp_included(dzp_included_count).x = x;
            dzp_included(dzp_included_count).y = y;
            dzp_included(dzp_included_count).outside_time = outside_time;
            dzp_included(dzp_included_count).outside_time_min = outside_time_min;
        end
    end

   
    subplot(nRow, nCol, i);
    plot(x, y, 'k-', 'LineWidth', 0.8);
    hold on;
    plot(100, 100, 'ro', 'MarkerSize', 4, 'MarkerFaceColor', 'r');
    theta = linspace(0, 2*pi, 200);
    circle_x = 100 + 40 * cos(theta);
    circle_y = 100 + 40 * sin(theta);
    plot(circle_x, circle_y, 'r--', 'LineWidth', 0.6);

    axis equal;
    xlim([60 250]);
    ylim([60 250]);
    set(gca, 'Color', 'w');
    axis off;
    title(sprintf('%.1f s', outside_time), ...
        'Interpreter', 'none', 'FontSize', 15, 'FontWeight', 'normal');
end

sgtitle('All mouse trajectories aligned to start point (100, 100)', 'FontSize', 16);

saveas(fig_all, fullfile(save_dir, 'all_mouse_trajectories_grouped_start_at_100_100.png'));



valid_rows = ~cellfun(@isempty, mouse_id_list);

result_table = table( ...
    mouse_id_list(valid_rows), ...
    group_list(valid_rows), ...
    outside_count_list(valid_rows), ...
    outside_time_list(valid_rows), ...
    outside_time_min_list(valid_rows), ...
    data_excluded_list(valid_rows), ...
    'VariableNames', {'MouseID', 'Group', 'Outside40cmPointCount', ...
    'Outside40cmTime_s', 'Outside40cmTime_min', 'DataExcluded'} ...
    );


disp(result_table);

writetable(result_table, fullfile(save_dir, 'outside_40cm_time_statistics_all.csv'));
writetable(result_table(strcmp(result_table.Group, 'veh'), :), ...
    fullfile(save_dir, 'outside_40cm_time_statistics_veh.csv'));
writetable(result_table(strcmp(result_table.Group, 'dzp'), :), ...
    fullfile(save_dir, 'outside_40cm_time_statistics_dzp.csv'));


%% =========================
%  pie chart of the VEH
%  =========================
veh_mask = strcmp(result_table.Group, 'veh');
veh_n_included = sum(veh_mask & ~result_table.DataExcluded);  % >5min
veh_n_excluded = sum(veh_mask & result_table.DataExcluded);   % <5min

if (veh_n_included + veh_n_excluded) > 0
    fig_pie_veh = figure('Visible', 'on', 'Color', 'w');
    set(fig_pie_veh, 'Position', [160, 160,550, 350]);

    veh_counts = [veh_n_included, veh_n_excluded];
    veh_total = sum(veh_counts);

    veh_pct_included = veh_n_included / veh_total * 100;
    veh_pct_excluded = veh_n_excluded / veh_total * 100;
    veh_texts = { ...
        sprintf('n=%d (%.1f%%)', veh_n_included, veh_pct_included), ...
        sprintf('n=%d (%.1f%%)', veh_n_excluded, veh_pct_excluded) ...
        };

    p = pie(veh_counts, veh_texts);

    patch_handles = findobj(gca, 'Type', 'Patch');

    if numel(patch_handles) >= 2
        patch_handles(2).FaceColor = blue_color;    % > 5 min
        patch_handles(1).FaceColor = orange_color;  % < 5 min
    end


    text_handles = findobj(gca, 'Type', 'Text');
    set(text_handles, 'FontSize', 14);

    legend({'> 5 min', '< 5 min'}, ...
        'Location', 'bestoutside', ...
        'FontSize', 14, ...
        'Box', 'off');

    title('Exploration time', ...
        'FontSize', 18, 'FontWeight', 'normal');

    set(gca, 'Color', 'w');

    saveas(fig_pie_veh, fullfile(save_dir, 'veh_outside40cm_time_pie.png'));
    saveas(fig_pie_veh, fullfile(save_dir, 'veh_outside40cm_time_pie.fig'));
else
    fprintf('No veh mice found for pie chart.\n');
end

%% =========================
%  pie chart of the DZP
%  =========================
dzp_mask = strcmp(result_table.Group, 'dzp');
dzp_n_included = sum(dzp_mask & ~result_table.DataExcluded);  % >5min
dzp_n_excluded = sum(dzp_mask & result_table.DataExcluded);   % <5min

if (dzp_n_included + dzp_n_excluded) > 0
    fig_pie_dzp = figure('Visible', 'on', 'Color', 'w');
    set(fig_pie_dzp, 'Position', [160, 160, 550, 350]);

    dzp_counts = [dzp_n_included, dzp_n_excluded];
    dzp_total = sum(dzp_counts);

    dzp_pct_included = dzp_n_included / dzp_total * 100;
    dzp_pct_excluded = dzp_n_excluded / dzp_total * 100;


    dzp_texts = { ...
        sprintf('n=%d (%.1f%%)', dzp_n_included, dzp_pct_included), ...
        sprintf('n=%d (%.1f%%)', dzp_n_excluded, dzp_pct_excluded) ...
        };

    p = pie(dzp_counts, dzp_texts);


    patch_handles = findobj(gca, 'Type', 'Patch');


    if numel(patch_handles) >= 2
        patch_handles(2).FaceColor = blue_color;    % > 5 min
        patch_handles(1).FaceColor = orange_color;  % < 5 min
    end


    text_handles = findobj(gca, 'Type', 'Text');
    set(text_handles, 'FontSize', 14);


    legend({'> 5 min', '< 5 min'}, ...
        'Location', 'bestoutside', ...
        'FontSize', 14, ...
        'Box', 'off');

    title('Exploration time', ...
        'FontSize', 18, 'FontWeight', 'normal');

    set(gca, 'Color', 'w');

    saveas(fig_pie_dzp, fullfile(save_dir, 'dzp_outside40cm_time_pie.png'));
    saveas(fig_pie_dzp, fullfile(save_dir, 'dzp_outside40cm_time_pie.fig'));
else
    fprintf('No dzp mice found for pie chart.\n');
end

fprintf('\nAll results saved in:\n%s\n', save_dir);

unknown_mask = strcmp(result_table.Group, 'unknown');
if any(unknown_mask)
    fprintf('\nWarning: The following mice were marked as UNKNOWN group:\n');
    disp(result_table.MouseID(unknown_mask));
end



%% =========================
%  Trajetory plot for 
%  DZP >5min, DZP <5min, VEH >5min, VEH <5min
%  
%  =========================

theta = linspace(0, 2*pi, 200);
circle_x = 100 + 40 * cos(theta);
circle_y = 100 + 40 * sin(theta);

%% -------- DZP > 5 min --------
nDzpIncluded = numel(dzp_included);

if nDzpIncluded > 0
    nCol_plot = 5;
    nRow_plot = ceil(nDzpIncluded / nCol_plot);

    fig_dzp_included = figure('Visible', 'on', 'Color', 'w');
    set(fig_dzp_included, 'Position', [100, 100, 1200, 600]);

    for k = 1:nDzpIncluded
        subplot(nRow_plot, nCol_plot, k);

        plot(dzp_included(k).x, dzp_included(k).y, 'k-', 'LineWidth', 0.8);
        hold on;
        plot(100, 100, 'ro', 'MarkerSize', 4, 'MarkerFaceColor', 'r');
        plot(circle_x, circle_y, 'r--', 'LineWidth', 0.6);

        axis equal;
        xlim([60 250]);
        ylim([60 250]);
        set(gca, 'Color', 'w');
        axis off;

        title(sprintf('%.1f s', dzp_included(k).outside_time), ...
            'Interpreter', 'none', 'FontSize', 15, 'FontWeight', 'normal');
    end

    sgtitle('>= 5 min', 'FontSize', 20);

    saveas(fig_dzp_included, fullfile(save_dir, 'dzp_included_trajectories_gt5min.png'));
  
else
    fprintf('No DZP trajectories > 5 min.\n');
end

%% -------- DZP < 5 min --------
nDzpExcluded = numel(dzp_excluded);

if nDzpExcluded > 0
    nCol_plot = 4;
    nRow_plot = ceil(nDzpExcluded / nCol_plot);

    fig_dzp_excluded = figure('Visible', 'on', 'Color', 'w');
    set(fig_dzp_excluded, 'Position', [120, 120, 1200, 600]);

    for k = 1:nDzpExcluded
        subplot(nRow_plot, nCol_plot, k);

        plot(dzp_excluded(k).x, dzp_excluded(k).y, 'k-', 'LineWidth', 0.8);
        hold on;
        plot(100, 100, 'ro', 'MarkerSize', 4, 'MarkerFaceColor', 'r');
        plot(circle_x, circle_y, 'r--', 'LineWidth', 0.6);

        axis equal;
        xlim([60 250]);
        ylim([60 250]);
        set(gca, 'Color', 'w');
        axis off;

        title(sprintf('%.1f s', dzp_excluded(k).outside_time), ...
            'Interpreter', 'none', 'FontSize', 15, 'FontWeight', 'normal');
    end

    sgtitle('< 5 min', 'FontSize', 20);

    saveas(fig_dzp_excluded, fullfile(save_dir, 'dzp_excluded_trajectories_lt5min.png'));
    
else
    fprintf('No DZP trajectories < 5 min.\n');
end

%% -------- VEH > 5 min --------
nVehIncluded = numel(veh_included);

if nVehIncluded > 0
    nCol_plot = 4;
    nRow_plot = ceil(nVehIncluded / nCol_plot);

    fig_veh_included = figure('Visible', 'on', 'Color', 'w');
    set(fig_veh_included, 'Position', [140, 140, 1200, 600]);

    for k = 1:nVehIncluded
        subplot(nRow_plot, nCol_plot, k);

        plot(veh_included(k).x, veh_included(k).y, 'k-', 'LineWidth', 0.8);
        hold on;
        plot(100, 100, 'ro', 'MarkerSize', 4, 'MarkerFaceColor', 'r');
        plot(circle_x, circle_y, 'r--', 'LineWidth', 0.6);

        axis equal;
        xlim([60 250]);
        ylim([60 250]);
        set(gca, 'Color', 'w');
        axis off;

        title(sprintf('%.1f s', veh_included(k).outside_time), ...
            'Interpreter', 'none', 'FontSize', 15, 'FontWeight', 'normal');
    end

    sgtitle('>= 5 min', 'FontSize', 20);

    saveas(fig_veh_included, fullfile(save_dir, 'veh_included_trajectories_gt5min.png'));
    saveas(fig_veh_included, fullfile(save_dir, 'veh_included_trajectories_gt5min.fig'));
else
    fprintf('No VEH trajectories > 5 min.\n');
end

%% -------- VEH < 5 min --------
nVehExcluded = numel(veh_excluded);

if nVehExcluded > 0
    nCol_plot = 4;
    nRow_plot = ceil(nVehExcluded / nCol_plot);

    fig_veh_excluded = figure('Visible', 'on', 'Color', 'w');
    set(fig_veh_excluded, 'Position', [160, 160, 1200, 600]);

    for k = 1:nVehExcluded
        subplot(nRow_plot, nCol_plot, k);

        plot(veh_excluded(k).x, veh_excluded(k).y, 'k-', 'LineWidth', 0.8);
        hold on;
        plot(100, 100, 'ro', 'MarkerSize', 4, 'MarkerFaceColor', 'r');
        plot(circle_x, circle_y, 'r--', 'LineWidth', 0.6);

        axis equal;
        xlim([60 250]);
        ylim([60 250]);
        set(gca, 'Color', 'w');
        axis off;

        title(sprintf('%.1f s', veh_excluded(k).outside_time), ...
            'Interpreter', 'none', 'FontSize', 15, 'FontWeight', 'normal');
    end

    sgtitle('< 5 min', 'FontSize', 20);

    saveas(fig_veh_excluded, fullfile(save_dir, 'veh_excluded_trajectories_lt5min.png'));
    saveas(fig_veh_excluded, fullfile(save_dir, 'veh_excluded_trajectories_lt5min.fig'));
else
    fprintf('No VEH trajectories < 5 min.\n');
end