package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class State extends JSONObject
	{
		// Constructor
		public function State(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "state";
		}
		
		// Data wrappers
		public function get User():Elixys.JSON.State.User
		{
			// Parse the user
			if (m_pUser == null)
			{
				m_pUser = new Elixys.JSON.State.User(null, super.flash_proxy::getProperty("user"));
			}
			return m_pUser;
		}
		public function get Timestamp():Number
		{
			return super.flash_proxy::getProperty("timestamp");
		}
		public function get ServerState():Elixys.JSON.State.ServerState
		{
			// Parse the server state
			if (m_pServerState == null)
			{
				m_pServerState = new Elixys.JSON.State.ServerState(null, super.flash_proxy::getProperty("serverstate"));
			}
			return m_pServerState;
		}
		public function get ClientState():Elixys.JSON.State.ClientState
		{
			// Parse the client state
			if (m_pClientState == null)
			{
				m_pClientState = new Elixys.JSON.State.ClientState(null, super.flash_proxy::getProperty("clientstate"));
			}
			return m_pClientState;
		}
		public function get Buttons():Array
		{
			// Parse the buttons
			if (m_pButtons == null)
			{
				m_pButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("buttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pButtons.push(pButton);
				}
			}
			return m_pButtons;
		}
		
		// State components
		protected var m_pUser:Elixys.JSON.State.User;
		protected var m_pServerState:Elixys.JSON.State.ServerState;
		protected var m_pClientState:Elixys.JSON.State.ClientState;
		protected var m_pButtons:Array;
	}
}
