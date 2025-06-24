<?xml version="1.0" encoding="utf-8"?>
<map version="1.0.1">
  <node TEXT="项目架构">
    <node TEXT="src">
      <node TEXT="__init__.py"/>
      <node TEXT="application">
        <node TEXT="__init__.py"/>
        <node TEXT="auto_login_and_test_service.py"/>
        <node TEXT="monitor">
          <node TEXT="resource_monitor_service.py"/>
        </node>
        <node TEXT="services">
          <node TEXT="api_send_service.py"/>
          <node TEXT="device_data_manager.py"/>
          <node TEXT="device_generator_service.py"/>
          <node TEXT="device_identifier_service.py"/>
          <node TEXT="device_query_application_service.py"/>
          <node TEXT="device_query_service.py"/>
          <node TEXT="jmx_parametrization_service.py"/>
          <node TEXT="performance_batch_service.py"/>
          <node TEXT="performance_test_service.py"/>
          <node TEXT="performance_tuning_service.py"/>
          <node TEXT="register_verification_service.py"/>
          <node TEXT="report_service.py"/>
        </node>
      </node>
      <node TEXT="config">
        <node TEXT="__init__.py"/>
        <node TEXT="config_manager.py"/>
      </node>
      <node TEXT="domain">
        <node TEXT="__init__.py"/>
        <node TEXT="entities">
          <node TEXT="device_info.py"/>
          <node TEXT="device_query.py"/>
          <node TEXT="report.py"/>
          <node TEXT="test_config.py"/>
          <node TEXT="test_result.py"/>
        </node>
        <node TEXT="monitor">
          <node TEXT="hardware_metrics.py"/>
          <node TEXT="hardware_monitor_report.py"/>
          <node TEXT="resource_snapshot.py"/>
          <node TEXT="test_summary.py"/>
        </node>
        <node TEXT="services">
          <node TEXT="device_identifier_generator.py"/>
          <node TEXT="device_query_domain_service.py"/>
        </node>
        <node TEXT="strategy">
          <node TEXT="performance_strategy.py"/>
        </node>
        <node TEXT="value_objects">
          <node TEXT="bulk_device_generator.py"/>
          <node TEXT="device_identifier.py"/>
          <node TEXT="query_criteria.py"/>
        </node>
      </node>
      <node TEXT="infrastructure">
        <node TEXT="__init__.py"/>
        <node TEXT="cross_cutting">
          <node TEXT="__init__.py"/>
          <node TEXT="analysis">
            <node TEXT="__init__.py"/>
            <node TEXT="performance_analyzer.py"/>
            <node TEXT="test_analyzer.py"/>
          </node>
          <node TEXT="configuration">
            <node TEXT="__init__.py"/>
          </node>
          <node TEXT="logging">
            <node TEXT="__init__.py"/>
            <node TEXT="logger.py"/>
          </node>
        </node>
        <node TEXT="external">
          <node TEXT="__init__.py"/>
          <node TEXT="file_system">
            <node TEXT="__init__.py"/>
            <node TEXT="report_generator.py"/>
          </node>
          <node TEXT="monitoring">
            <node TEXT="__init__.py"/>
            <node TEXT="excel_report_generator.py"/>
            <node TEXT="remote_resource_collector.py"/>
            <node TEXT="report_generator.py"/>
          </node>
          <node TEXT="testing_tools">
            <node TEXT="__init__.py"/>
          </node>
        </node>
        <node TEXT="persistence">
          <node TEXT="__init__.py"/>
          <node TEXT="database">
            <node TEXT="__init__.py"/>
            <node TEXT="db_client.py"/>
          </node>
          <node TEXT="repositories">
            <node TEXT="__init__.py"/>
            <node TEXT="device_identifier_repository.py"/>
            <node TEXT="device_repository.py"/>
            <node TEXT="strategy_repository.py"/>
          </node>
        </node>
        <node TEXT="services">
          <node TEXT="__init__.py"/>
          <node TEXT="authentication">
            <node TEXT="__init__.py"/>
            <node TEXT="login_service.py"/>
          </node>
          <node TEXT="testing">
            <node TEXT="__init__.py"/>
            <node TEXT="api_test_service.py"/>
          </node>
          <node TEXT="utilities">
            <node TEXT="__init__.py"/>
            <node TEXT="redis_service.py"/>
            <node TEXT="uuid_service.py"/>
          </node>
        </node>
      </node>
      <node TEXT="interfaces">
        <node TEXT="__init__.py"/>
        <node TEXT="cli">
          <node TEXT="db_query_cli.py"/>
          <node TEXT="device_generator_cli.py"/>
          <node TEXT="jmx_parametrization_cli.py"/>
          <node TEXT="manual_register_test.py"/>
          <node TEXT="performance_test_cli copy.py"/>
          <node TEXT="performance_test_cli.py"/>
          <node TEXT="performance_tuning_cli.py"/>
          <node TEXT="register_param_sweep.py"/>
          <node TEXT="register_param_sweep_simple.py"/>
          <node TEXT="register_test_cli.py"/>
          <node TEXT="register_verification_cli.py"/>
          <node TEXT="resource_monitor_cli.py"/>
          <node TEXT="simple_register_test_cli.py"/>
        </node>
        <node TEXT="main_auto_login_and_test copy.py"/>
        <node TEXT="main_auto_login_and_test.py"/>
      </node>
      <node TEXT="tools">
        <node TEXT="__init__.py"/>
        <node TEXT="create_parametrized_jmx.py"/>
        <node TEXT="generators">
          <node TEXT="__init__.py"/>
          <node TEXT="migrate_ddd.py"/>
          <node TEXT="project_template.py"/>
          <node TEXT="utils">
            <node TEXT="__init__.py"/>
            <node TEXT="config_utils.py"/>
            <node TEXT="file_utils.py"/>
            <node TEXT="logging_utils.py"/>
            <node TEXT="template_utils.py"/>
          </node>
        </node>
        <node TEXT="monitor">
          <node TEXT="setup.py"/>
          <node TEXT="tests">
            <node TEXT="create_test_files.py"/>
            <node TEXT="test_alert_handler.py"/>
            <node TEXT="test_analyzers.py"/>
            <node TEXT="test_collectors.py"/>
            <node TEXT="test_notifiers.py"/>
            <node TEXT="test_system.py"/>
          </node>
          <node TEXT="web">
            <node TEXT="app.py"/>
          </node>
        </node>
      </node>
    </node>
    <node TEXT="scripts">
      <node TEXT="__init__.py"/>
      <node TEXT="analyze_jtl_timing.py"/>
      <node TEXT="api_test_flow.py"/>
      <node TEXT="batch_insert_devices.py"/>
      <node TEXT="batch_login_test.py"/>
      <node TEXT="batch_register_test.py"/>
      <node TEXT="enhanced_hardware_monitoring.py"/>
      <node TEXT="excel_to_csv.py"/>
      <node TEXT="generate_external_report.py"/>
      <node TEXT="generate_internal_analysis_report.py"/>
      <node TEXT="generate_jmeter_test.py"/>
      <node TEXT="generate_meeting_import_csv.py"/>
      <node TEXT="generate_meeting_schedule.py"/>
      <node TEXT="generate_project_mindmap_freemind.py"/>
      <node TEXT="generate_project_mindmap_graphviz.py"/>
      <node TEXT="generate_project_mindmap_pyecharts_auto.py"/>
      <node TEXT="generate_uuid.py"/>
      <node TEXT="init_project.py"/>
      <node TEXT="jmeter_auto_test.py"/>
      <node TEXT="jmeter_batch_register.py"/>
      <node TEXT="jmeter_batch_register_enhanced copy.py"/>
      <node TEXT="jmeter_batch_register_enhanced.py"/>
      <node TEXT="jmeter_consistency_verification.py"/>
      <node TEXT="jmeter_csv_report.py"/>
      <node TEXT="jmeter_plan_filter.py"/>
      <node TEXT="jmeter_report_manager.py"/>
      <node TEXT="jmeter_result_filter_and_report.py"/>
      <node TEXT="performance_stress_test_plan.py"/>
      <node TEXT="performance_test_orchestrator.py"/>
      <node TEXT="phase1_reconnaissance.py"/>
      <node TEXT="project_mindmap_demo_matplotlib.py"/>
      <node TEXT="project_mindmap_pyecharts.py"/>
      <node TEXT="project_mindmap_to_png.py"/>
      <node TEXT="python">
        <node TEXT="fix_infrastructure_structure.py"/>
        <node TEXT="refactor_infrastructure.py"/>
      </node>
      <node TEXT="read_excel.py"/>
      <node TEXT="split_csv_to_parts.py"/>
      <node TEXT="test_redis_connection.py"/>
      <node TEXT="test_single_part.py"/>
      <node TEXT="test_uuid.py"/>
      <node TEXT="update_config_references.py"/>
      <node TEXT="update_jmx_files.py"/>
      <node TEXT="verify_hardware_monitoring.py"/>
      <node TEXT="verify_parts.py"/>
    </node>
  </node>
</map>
