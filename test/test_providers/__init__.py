def check_invalid_request_log(caplog):
    assert len(caplog.records) == 1
    assert "Error sending HTTP request" in caplog.records[0].message
    record_dict = caplog.records[0].__dict__

    assert "request" in record_dict
    assert "method" in record_dict["request"]
    assert "url" in record_dict["request"]
    assert "data" in record_dict["request"]
    assert "params" in record_dict["request"]

    assert "response" in record_dict
    assert "status_code" in record_dict["response"]
    assert "response_body" in record_dict["response"]
    assert "response_headers" in record_dict["response"]
