package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class State extends JSONObject
	{
		// Constructor
		public function State(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function User():Elixys.Objects.User
		{
			// Parse the user
			if (m_pUser == null)
			{
				m_pUser = new Elixys.Objects.User(null, super.flash_proxy::getProperty("user"));
			}
			return m_pUser;
		}
		public function ServerState():Elixys.Objects.ServerState
		{
			// Parse the server state
			if (m_pServerState == null)
			{
				m_pServerState = new Elixys.Objects.ServerState(null, super.flash_proxy::getProperty("serverstate"));
			}
			return m_pServerState;
		}
		public function ClientState():Elixys.Objects.ClientState
		{
			// Parse the client state
			if (m_pClientState == null)
			{
				m_pClientState = new Elixys.Objects.ClientState(null, super.flash_proxy::getProperty("clientstate"));
			}
			return m_pClientState;
		}
		public function NavigationButtons():Array
		{
			// Parse the buttons
			if (m_pNavigationButtons == null)
			{
				m_pNavigationButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("navigationbuttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pNavigationButtons.push(pButton);
				}
			}
			return m_pNavigationButtons;
		}
		
		// Type
		static public var TYPE:String = "state";
		
		// State components
		private var m_pUser:Elixys.Objects.User;
		private var m_pServerState:Elixys.Objects.ServerState;
		private var m_pClientState:Elixys.Objects.ClientState;
		private var m_pNavigationButtons:Array;
	}
}
