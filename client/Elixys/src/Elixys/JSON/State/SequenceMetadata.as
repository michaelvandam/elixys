package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class SequenceMetadata extends JSONObject
	{
		// Constructor
		public function SequenceMetadata(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = m_sDefault;
			}
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
			return "sequencemetadata";
		}

		// Copy
		public function Copy(pSourceSequence:SequenceMetadata):void
		{
			Name = pSourceSequence.Name;
			Time = pSourceSequence.Time;
			Date = pSourceSequence.Date;
			Comment = pSourceSequence.Comment;
			ID = pSourceSequence.ID;
			Creator = pSourceSequence.Creator;
			Operations = pSourceSequence.Operations;
		}
		
		// Data wrappers
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function set Name(value:String):void
		{
			super.flash_proxy::setProperty("name", value);
		}
		public function get Time():String
		{
			return super.flash_proxy::getProperty("time");
		}
		public function set Time(value:String):void
		{
			super.flash_proxy::setProperty("time", value);
		}
		public function get Date():String
		{
			return super.flash_proxy::getProperty("date");
		}
		public function set Date(value:String):void
		{
			super.flash_proxy::setProperty("date", value);
		}
		public function get Comment():String
		{
			return super.flash_proxy::getProperty("comment");
		}
		public function set Comment(value:String):void
		{
			super.flash_proxy::setProperty("comment", value);
		}
		public function get ID():uint
		{
			return super.flash_proxy::getProperty("id");
		}
		public function set ID(value:uint):void
		{
			super.flash_proxy::setProperty("id", value);
		}
		public function get Creator():String
		{
			return super.flash_proxy::getProperty("creator");
		}
		public function set Creator(value:String):void
		{
			super.flash_proxy::setProperty("creator", value);
		}
		public function get Operations():uint
		{
			return parseInt(super.flash_proxy::getProperty("operations"));
		}
		public function set Operations(value:uint):void
		{
			super.flash_proxy::setProperty("operations", value);
		}
		
		// Sequence metadata comparison function.  Returns true if the sequences are equal, false otherwise.
		public static function CompareSequences(pSequenceA:SequenceMetadata, pSequenceB:SequenceMetadata):Boolean
		{
			if (pSequenceA.Name != pSequenceB.Name)
			{
				return false;
			}
			if (pSequenceA.Time != pSequenceB.Time)
			{
				return false;
			}
			if (pSequenceA.Date != pSequenceB.Date)
			{
				return false;
			}
			if (pSequenceA.Comment != pSequenceB.Comment)
			{
				return false;
			}
			if (pSequenceA.ID != pSequenceB.ID)
			{
				return false;
			}
			if (pSequenceA.Creator != pSequenceB.Creator)
			{
				return false;
			}
			if (pSequenceA.Operations != pSequenceB.Operations)
			{
				return false;
			}
			return true;
		}
		
		// Sequence metadata array comparison function.  Returns true if the arrays are equal, false otherwise.
		public static function CompareSequenceArrays(pSequencesA:Array, pSequencesB:Array):Boolean
		{
			if (pSequencesA.length != pSequencesB.length)
			{
				return false;
			}
			else
			{
				var pSequenceA:SequenceMetadata, pSequenceB:SequenceMetadata;
				for (var i:int = 0; i < pSequencesA.length; ++i)
				{
					pSequenceA = pSequencesA[i] as SequenceMetadata;
					pSequenceB = pSequencesB[i] as SequenceMetadata;
					if (!CompareSequences(pSequenceA, pSequenceB))
					{
						return false;
					}
				}
			}
			return true;
		}
		
		// Default format
		protected var m_sDefault:String = "{ \"type\":\"sequencemetadata\", \"name\":\"\", \"time\":\"\", \"date\":\"\", " +
			"\"comment\":\"\", \"id\":\"\", \"creator\":\"\", \"operations\":\"\" }";
	}
}
